#!/usr/bin/env python3

import serial
import re
import time
import paho.mqtt.client as mqtt
import argparse
import sys
import json
import socket
import threading
import os
import netrc

def get_machine_id_suffix():
    """Return last 4 hex digits of /etc/machine-id or cpuinfo serial"""
    try:
        with open("/etc/machine-id", "r") as f:
            mid = f.read().strip()
            if len(mid) >= 8:
                return mid[-8]
    except:
        pass
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if line.startswith("Serial"):
                    serial = line.split(":")[1].strip()
                    if len(serial) >= 8:
                        return serial[-8:-4].lower()
    except:
        pass
    return "0000"  # fallback

class IBootBar:
    def __init__(self, port="/dev/ttyUSB0", baudrate=115200, timeout=5, debug=False):
        self.debug = debug
        self.prompt = b'SBB> '
        try:
            self.ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=timeout
            )
            self.ser.flushInput()
            self.ser.flushOutput()
            time.sleep(0.5)
            self._log("Serial port opened:", port)
            self._sync_prompt()
        except serial.SerialException as e:
            print(f"Error opening serial port {port}: {e}")
            sys.exit(1)

    def _log(self, *args):
        if self.debug:
            print("SERIAL DEBUG:", *args)

    def _sync_prompt(self):
        self.ser.write(b'\r\n')
        time.sleep(0.1)
        self.ser.read_all()

    def _send_command(self, cmd):
        full_cmd = cmd + '\r\n'
        self._log(">>>", full_cmd.strip())
        self.ser.write(full_cmd.encode('utf-8'))
        self.ser.flush()

    def _read_response(self):
        try:
            data = self.ser.read_until(self.prompt)
            response = data.decode('utf-8', errors='ignore')
            if response.endswith('SBB> '):
                response = response[:-5]
            response = response.strip()
            self._log("<<<", repr(response) if response else "(empty)")
            return response
        except Exception as e:
            self._log("Read error:", e)
            return ""

    def _wait_for_prompt(self):
        self.ser.write(b'\r\n')
        time.sleep(0.05)
        self.ser.read_until(self.prompt)

    def set_outlet(self, number, state):
        if not 1 <= number <= 8:
            raise ValueError("Outlet number must be 1-8")
        state = state.capitalize()
        cmd = f"set outlet {number} {state.lower()}"
        max_retries = 4
        for attempt in range(max_retries):
            self._wait_for_prompt()
            self._send_command(cmd)
            response = self._read_response()
            if "OK" in response.upper():
                if self.get_outlet_state(number) == state:
                    self._log(f"Outlet {number} → {state}")
                    return True
            time.sleep(0.5)
        raise Exception(f"Failed to set outlet {number}")

    def get_outlet_state(self, number):
        cmd = f"get outlet {number}"
        max_retries = 4
        for attempt in range(max_retries):
            self._wait_for_prompt()
            self._send_command(cmd)
            response = self._read_response()
            if "OK" in response.upper():
                m = re.search(r'\b(On|Off)\b', response, re.IGNORECASE)
                if m:
                    return m.group(1).capitalize()
            time.sleep(0.5)
        raise Exception(f"Failed to read outlet {number}")

    def get_all_outlets(self):
        max_retries = 3
        for attempt in range(max_retries):
            self._wait_for_prompt()
            self._send_command("get outlets")
            response = self._read_response()
            if "OK" in response.upper() and "Outlet" in response:
                result = {}
                for line in response.split('\n'):
                    line = line.strip()
                    if not line or not line[0].isdigit():
                        continue
                    parts = line.split()
                    num = int(parts[0])
                    state = parts[-1].capitalize()
                    result[num] = {"state": state}
                if result:
                    return result
            time.sleep(0.6)
        raise Exception("Failed to get all outlets")


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


# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    if rc != 0:
        print(f"MQTT connect failed: {rc}")
        return
    print("Connected to MQTT broker")

    prefix = userdata['mqtt_prefix']
    device_info = userdata['device_info']
    max_outlet = userdata['max_outlet']

    # Register switches
    for i in range(1, max_outlet + 1):
        client.publish(f"homeassistant/switch/{prefix}_outlet_{i}/config", json.dumps({
            "name": f"iBootBar Outlet {i}",
            "unique_id": f"{prefix}_outlet_{i}",
            "command_topic": f"{prefix}/outlet_{i}/set",
            "state_topic": f"{prefix}/outlet_{i}/state",
            "payload_on": "ON",
            "payload_off": "OFF",
            "qos": 1,
            "device": device_info,
            "availability_topic": f"{prefix}/availability"
        }), retain=True)
        client.subscribe(f"{prefix}/outlet_{i}/set")

    # IP sensor
    client.publish(f"homeassistant/sensor/{prefix}_ip/config", json.dumps({
        "name": "iBootBar Pi IP",
        "unique_id": f"{prefix}_ip",
        "state_topic": f"{prefix}/ip/state",
        "icon": "mdi:ip-network",
        "device": device_info,
        "availability_topic": f"{prefix}/availability"
    }), retain=True)

    client.publish(f"{prefix}/availability", "online", retain=True)
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


def publish_states(client, userdata):
    ibootbar = userdata['ibootbar']
    prefix = userdata['mqtt_prefix']
    max_outlet = userdata['max_outlet']
    try:
        states = ibootbar.get_all_outlets()
        for i in range(1, max_outlet + 1):
            state = states.get(i, {}).get("state", "OFF").upper()
            client.publish(f"{prefix}/outlet_{i}/state", state, retain=True)
    except Exception as e:
        print("State update failed:", e)
    client.publish(f"{prefix}/ip/state", get_local_ip())


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
    parser.add_argument("--mqtt_host", required=True, help="MQTT broker (as in .netrc)")
    parser.add_argument("--mqtt_port", type=int, default=1883)
    parser.add_argument("--serial_port", default="/dev/ttyUSB0")
    parser.add_argument("--mqtt_prefix", help="Custom prefix (default: ibootbar_XXXX)")
    parser.add_argument("--include-port8", action="store_true", help="Also expose outlet 8 (default: hidden)")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--undiscover", action="store_true")
    args = parser.parse_args()

    suffix = get_machine_id_suffix()
    prefix = args.mqtt_prefix or f"ibootbar_{suffix}"
    max_outlet = 8 if args.include_port8 else 7

    print(f"Starting iBootBar bridge")
    print(f"   Prefix   : {prefix}")
    print(f"   Outlets  : 1–{max_outlet} {'(8 hidden)' if not args.include_port8 else '(8 included)'}")
    print(f"   Serial   : {args.serial_port}")

    ibootbar = IBootBar(port=args.serial_port, debug=args.debug)

    device_info = {
        "identifiers": [f"ibootbar_{suffix}"],
        "name": "iBootBar Power Strip",
        "model": "iBoot-Bar",
        "manufacturer": "Dataprobe",
        "sw_version": "1.2"
    }

    userdata = {
        "ibootbar": ibootbar,
        "mqtt_prefix": prefix,
        "device_info": device_info,
        "max_outlet": max_outlet
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
    client.loop_forever()


if __name__ == "__main__":
    main()
