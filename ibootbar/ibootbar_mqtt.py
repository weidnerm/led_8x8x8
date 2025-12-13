#!/usr/bin/env python3
import sys
sys.stdout.reconfigure(line_buffering=True)  # Force immediate print flushing
import serial
import re
import time
import paho.mqtt.client as mqtt
import argparse
import json
import socket
import threading
import queue
import os
import netrc

# 1. Add this helper at the top (after imports)
def debug_print(client, topic, payload):
    if client.userdata and client.userdata.get('debug', False):
        print(f"MQTT PUBLISH → {topic} : {payload}")
        
def get_machine_id_suffix():
    try:
        with open("/etc/machine-id", "r") as f:
            mid = f.read().strip()
            if len(mid) == 32:
                return mid[-8:]
    except Exception:
        pass
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if line.startswith("Serial"):
                    serial = line.split(":")[1].strip()
                    serial_clean = serial.lstrip("0") or "0"
                    return serial_clean[-8:].lower()
    except Exception:
        pass
    return "00000000"

# ────────────────────── Thread-safe serial worker ──────────────────────
class SerialWorker(threading.Thread):
    def __init__(self, port="/dev/ttyUSB0", debug=False):
        super().__init__(daemon=True)
        self.debug = debug
        self.port = port
        self.queue = queue.Queue()
        self.start()

    def run(self):
        try:
            ser = serial.Serial(
                port=self.port,
                baudrate=115200,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            ser.flushInput()
            ser.flushOutput()
            print("TIME DEBUG: time.sleep(0.5)")
            time.sleep(0.5)
            if self.debug:
                print("SERIAL DEBUG: Serial port opened:", self.port)
            ser.write(b'\r')
            print("TIME DEBUG: time.sleep(0.1)")
            time.sleep(0.1)
            ser.read_all()
        except Exception as e:
            print(f"Serial open failed: {e}")
            return

        prompt = b'SBB> '

        while True:
            job = self.queue.get()
            if job is None:          # shutdown signal
                ser.close()
                break

            cmd, result_q = job

            try:
                if self.debug:
                    print("SERIAL DEBUG: >>>", cmd.strip())
                ser.write((cmd + '\r').encode('utf-8'))
                ser.flush()

                data = ser.read_until(prompt)
                resp = data.decode('utf-8', errors='ignore')
                if resp.endswith('SBB> '):
                    resp = resp[:-5].strip()
                else:
                    resp = resp.strip()

                if self.debug:
                    print("SERIAL DEBUG: <<<", repr(resp) if resp else "(empty)")

                result_q.put(("OK", resp))
            except Exception as e:
                result_q.put(("ERROR", str(e)))

    def execute(self, command):
        result_q = queue.Queue()
        self.queue.put((command, result_q))
        status, resp = result_q.get()
        return status, resp

# ────────────────────── IBootBar using the worker ──────────────────────
class IBootBar:
    def __init__(self, port="/dev/ttyUSB0", debug=False):
        self.worker = SerialWorker(port=port, debug=debug)

    def _exec(self, cmd):
        status, resp = self.worker.execute(cmd)
        if status != "OK":
            raise Exception(f"Serial error: {resp}")
        return resp

    # ~ def _wait_for_prompt(self):
        # ~ self._exec("")

    def set_outlet(self, number, state):
        if not 1 <= number <= 8:
            raise ValueError("Outlet number must be 1-8")
        state = state.capitalize()
        cmd = f"set outlet {number} {state.lower()}"
        for _ in range(4):
            # ~ self._wait_for_prompt()()
            resp = self._exec(cmd)
            if "OK" in resp.upper():
                if self.get_outlet_state(number) == state:
                    return True
            print("TIME DEBUG: time.sleep(0.5)")
            time.sleep(0.5)
        raise Exception(f"Failed to set outlet {number}")

    def get_outlet_state(self, number):
        cmd = f"get outlet {number}"
        for _ in range(4):
            # ~ self._wait_for_prompt()()
            resp = self._exec(cmd)
            if "OK" in resp.upper():
                m = re.search(r'\b(On|Off)\b', resp, re.IGNORECASE)
                if m:
                    return m.group(1).capitalize()
            print("TIME DEBUG: time.sleep(0.5)")
            time.sleep(0.5)
        raise Exception(f"Failed to read outlet {number}")

    def get_all_outlets(self):
        for _ in range(3):
            # ~ self._wait_for_prompt()()
            resp = self._exec("get outlets").replace('Outlets:', '')
            if "OK" in resp.upper() and "Outlet" in resp:
                result = {}
                for raw_line in resp.split('\n'):
                    line = raw_line.strip()
                    # Skip header line and empty lines
                    if not line or line.startswith("Outlets:"):
                        continue
                    # Handle possible leading spaces
                    clean = line.lstrip()
                    if not clean or not clean[0].isdigit():
                        continue
                    parts = clean.split()
                    if len(parts) < 3:
                        continue
                    num = int(parts[0])
                    state = parts[-1].capitalize()
                    result[num] = {"state": state}
                if result:
                    return result
            print("TIME DEBUG: time.sleep(0.6)")
            time.sleep(0.6)
        raise Exception("Failed to get all outlets")
        

# ────────────────────── Rest of your original code (unchanged) ──────────────────────
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

class MQTTBridge:
    def read_netrc(self, filename=None):
        if filename is None:
            filename = os.path.expanduser("/home/pi/.netrc")
        try:
            return netrc.netrc(filename).hosts
        except Exception as e:
            print(f"Could not read .netrc: {e}")
            return {}
    def get_credentials(self, machine):
        hosts = self.read_netrc()
        if machine in hosts:
            login, _, password = hosts[machine]
            return login, password
        return None, None
    def mqtt_connect(self, client, mqtt_host):
        username, password = self.get_credentials(mqtt_host)
        if username and password:
            client.username_pw_set(username, password)
            print(f"Using .netrc credentials for {mqtt_host}")
        else:
            print("No credentials in .netrc → connecting anonymously")

def on_connect(client, userdata, flags, rc):
    if rc != 0:
        print(f"MQTT connect failed: {rc}")
        return
    print("Connected to MQTT broker")

    prefix = userdata['mqtt_prefix']
    device_info = userdata['device_info']
    max_outlet = userdata['max_outlet']
    debug = userdata.get('debug', False)

    # === RE-PUBLISH DISCOVERY ON EVERY CONNECT (fixes boot race) ===
    # Small delay to let broker/HA settle
    time.sleep(2)

    for i in range(1, max_outlet + 1):
        config_topic = f"homeassistant/switch/{prefix}_outlet_{i}/config"
        payload = json.dumps({
            "name": f"iBootBar Outlet {i}",
            "unique_id": f"{prefix}_outlet_{i}",
            "command_topic": f"{prefix}/outlet_{i}/set",
            "state_topic": f"{prefix}/outlet_{i}/state",
            "payload_on": "ON",
            "payload_off": "OFF",
            "qos": 1,
            "device": device_info,
            "availability_topic": f"{prefix}/availability"
        })
        client.publish(config_topic, payload, retain=True)
        if debug:
            print(f"MQTT DISCOVERY → {config_topic}")
        client.subscribe(f"{prefix}/outlet_{i}/set")

    ip_config_topic = f"homeassistant/sensor/{prefix}_ip/config"
    client.publish(ip_config_topic, json.dumps({
        "name": "iBootBar Pi IP",
        "unique_id": f"{prefix}_ip",
        "state_topic": f"{prefix}/ip/state",
        "icon": "mdi:ip-network",
        "device": device_info,
        "availability_topic": f"{prefix}/availability"
    }), retain=True)
    if debug:
        print(f"MQTT DISCOVERY → {ip_config_topic}")

    # === SEND AVAILABILITY ONLINE ===
    client.publish(f"{prefix}/availability", "online", retain=True)
    if debug:
        print(f"MQTT AVAILABILITY → {prefix}/availability : online")

    # Initial state push
    publish_states(client, userdata)
    
    
def on_message(client, userdata, msg):
    prefix = userdata['mqtt_prefix']
    max_outlet = userdata['max_outlet']
    ibootbar = userdata['ibootbar']
    payload = msg.payload.decode().strip().upper()
    for i in range(1, max_outlet + 1):
        if msg.topic == f"{prefix}/outlet_{i}/set" and payload in ["ON", "OFF"]:
            try:
                ibootbar.set_outlet(i, payload)
                state = ibootbar.get_outlet_state(i)
                client.publish(f"{prefix}/outlet_{i}/state", state.upper(), retain=True)
            except Exception as e:
                print(f"Outlet {i} error: {e}")
            break

# 2. Replace your publish_states() function with this version:
def publish_states(client, userdata):
    ibootbar = userdata['ibootbar']
    prefix = userdata['mqtt_prefix']
    max_outlet = userdata['max_outlet']
    debug = userdata.get('debug', False)  # <-- added

    try:
        states = ibootbar.get_all_outlets()
        for i in range(1, max_outlet + 1):
            raw_state = states.get(i, {}).get("state", "OFF")
            state_upper = raw_state.upper()  # <-- force uppercase
            topic = f"{prefix}/outlet_{i}/state"
            client.publish(topic, state_upper, retain=True)
            if debug:
                print(f"MQTT PUBLISH → {topic} : {state_upper}")
    except Exception as e:
        print("State update failed:", e)

    ip_topic = f"{prefix}/ip/state"
    client.publish(ip_topic, get_local_ip())
    if debug:
        print(f"MQTT PUBLISH → {ip_topic} : {get_local_ip()}")
        
    client.publish(f"{prefix}/availability", "online", retain=True)
    if debug:
        print(f"MQTT PUBLISH → {prefix}/availability : online")

    
def polling_thread(client, userdata):
    while True:
        publish_states(client, userdata)
        time.sleep(12)

def undiscover(client, userdata):
    prefix = userdata['mqtt_prefix']
    max_outlet = userdata['max_outlet']
    for i in range(1, max_outlet + 1):
        client.publish(f"homeassistant/switch/{prefix}_outlet_{i}/config", "", retain=True)
    client.publish(f"homeassistant/sensor/{prefix}_ip/config", "", retain=True)
    client.publish(f"{prefix}/availability", "offline", retain=True)
    print("Undiscovery sent.")

def main():
    parser = argparse.ArgumentParser(description="iBootBar → Home Assistant (MQTT)")
    parser.add_argument("--mqtt_host", required=True)
    parser.add_argument("--mqtt_port", type=int, default=1883)
    parser.add_argument("--serial_port", default="/dev/ttyUSB0")
    parser.add_argument("--mqtt_prefix")
    parser.add_argument("--include-port8", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--undiscover", action="store_true")
    args = parser.parse_args()

    suffix = get_machine_id_suffix()
    prefix = args.mqtt_prefix or f"ibootbar_{suffix}"
    max_outlet = 8 if args.include_port8 else 7

    print(f"Starting iBootBar bridge")
    print(f" Prefix : {prefix}")
    print(f" Outlets : 1–{max_outlet} {'(8 hidden)' if not args.include_port8 else '(8 included)'}")
    print(f" Serial : {args.serial_port}")

    ibootbar = IBootBar(port=args.serial_port, debug=args.debug)

    device_info = {
        "identifiers": [f"ibootbar_{suffix}"],
        "name": "iBootBar Power Strip",
        "model": "iBoot-Bar",
        "manufacturer": "Dataprobe",
        "sw_version": "1.4-threadsafe"
    }

    userdata = {
        "ibootbar": ibootbar,
        "mqtt_prefix": prefix,
        "device_info": device_info,
        "max_outlet": max_outlet,
        "debug": args.debug          # ← ADD THIS LINE
    }

    client = mqtt.Client(userdata=userdata)
    client.on_connect = on_connect
    client.on_message = on_message
    client.will_set(f"{prefix}/availability", "offline", retain=True)

    MQTTBridge().mqtt_connect(client, args.mqtt_host)

    try:
        client.connect(args.mqtt_host, args.mqtt_port, 60)
    except Exception as e:
        print(f"MQTT connection failed: {e}")
        sys.exit(1)

    if args.undiscover:
        client.loop_start()
        time.sleep(2)
        undiscover(client, userdata)
        time.sleep(2)
        client.loop_stop()
        sys.exit(0)

    threading.Thread(target=polling_thread, args=(client, userdata), daemon=True).start()
    try:
        client.loop_forever()
    finally:
        if hasattr(ibootbar, 'worker'):
            ibootbar.worker.queue.put(None)
            ibootbar.worker.join(timeout=2)

if __name__ == "__main__":
    main()
