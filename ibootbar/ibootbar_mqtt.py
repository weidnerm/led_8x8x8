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
            self._sync_prompt()  # Ensure we start clean
        except serial.SerialException as e:
            print(f"Error opening serial port {port}: {e}")
            sys.exit(1)

    def _log(self, *args):
        if self.debug:
            print("SERIAL DEBUG:", *args)

    def _sync_prompt(self):
        """Send CR and drain until we see the prompt (or timeout)"""
        self.ser.write(b'\r\n')
        time.sleep(0.1)
        self.ser.read_all()  # Clear any junk

    def _send_command(self, cmd):
        full_cmd = cmd + '\r\n'
        self._log(">>>", full_cmd.strip())
        self.ser.write(full_cmd.encode('utf-8'))
        self.ser.flush()

    def _read_response(self):
        """Wait specifically for the SBB> prompt – fast and reliable"""
        try:
            data = self.ser.read_until(self.prompt)
            response = data.decode('utf-8', errors='ignore')
            # Remove the prompt itself from output
            if response.endswith('SBB> '):
                response = response[:-5]
            response = response.strip()
            self._log("<<<", repr(response) if response else "(empty)")
            return response
        except Exception as e:
            self._log("Read error:", e)
            return ""

    def _wait_for_prompt(self):
        """Ensure we're at a clean prompt before sending next command"""
        self.ser.write(b'\r\n')
        time.sleep(0.05)
        self.ser.read_until(self.prompt)

    def set_outlet(self, number, state):
        if not 1 <= number <= 8:
            raise ValueError("Outlet number must be 1-8")
        state = state.capitalize()
        if state not in ["On", "Off"]:
            raise ValueError("State must be 'on' or 'off'")

        cmd = f"set outlet {number} {state.lower()}"
        max_retries = 4

        for attempt in range(max_retries):
            self._wait_for_prompt()
            self._send_command(cmd)
            response = self._read_response()

            if "OK" in response.upper():
                current = self.get_outlet_state(number)
                if current == state:
                    self._log(f"Outlet {number} set to {state}")
                    return True
                else:
                    self._log(f"Verification failed: expected {state}, got {current}")
            else:
                self._log(f"Command failed: {response}")

            time.sleep(0.5)

        raise Exception(f"Failed to set outlet {number} to {state}")

    def get_outlet_state(self, number):
        cmd = f"get outlet {number}"
        max_retries = 4

        for attempt in range(max_retries):
            self._wait_for_prompt()
            self._send_command(cmd)
            response = self._read_response()

            if "OK" in response.upper():
                match = re.search(r'\b(On|Off)\b', response, re.IGNORECASE)
                if match:
                    state = match.group(1).capitalize()
                    self._log(f"Outlet {number} is {state}")
                    return state

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
                    name = " ".join(parts[1:-1]) if len(parts) > 2 else f"Outlet{num}"
                    result[num] = {"name": name, "state": state}
                if result:
                    return result
            time.sleep(0.6)

        raise Exception("Failed to get all outlets")


# === Rest of the MQTT code unchanged except for debug flag ===

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


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        ibootbar = userdata['ibootbar']
        mqtt_prefix = userdata['mqtt_prefix']
        device_info = userdata['device_info']

        for i in range(1, 9):
            config_topic = f"homeassistant/switch/{mqtt_prefix}_outlet_{i}/config"
            payload = {
                "name": f"iBootBar Outlet {i}",
                "unique_id": f"{mqtt_prefix}_outlet_{i}",
                "command_topic": f"{mqtt_prefix}/outlet_{i}/set",
                "state_topic": f"{mqtt_prefix}/outlet_{i}/state",
                "payload_on": "ON",
                "payload_off": "OFF",
                "qos": 1,
                "retain": False,
                "device": device_info,
                "availability_topic": f"{mqtt_prefix}/availability",
                "payload_available": "online",
                "payload_not_available": "offline"
            }
            client.publish(config_topic, json.dumps(payload), retain=True)
            client.subscribe(f"{mqtt_prefix}/outlet_{i}/set")

        # IP Address Sensor
        client.publish(f"homeassistant/sensor/{mqtt_prefix}_ip/config", json.dumps({
            "name": "iBootBar Pi IP Address",
            "unique_id": f"{mqtt_prefix}_ip",
            "state_topic": f"{mqtt_prefix}/ip/state",
            "icon": "mdi:ip-network",
            "device": device_info,
            "availability_topic": f"{mqtt_prefix}/availability"
        }), retain=True)

        client.publish(f"{mqtt_prefix}/availability", "online", retain=True)
        publish_states(client, userdata)
    else:
        print(f"MQTT connection failed: {rc}")


def on_message(client, userdata, msg):
    ibootbar = userdata['ibootbar']
    mqtt_prefix = userdata['mqtt_prefix']
    payload = msg.payload.decode('utf-8').strip().upper()

    for i in range(1, 9):
        if msg.topic == f"{mqtt_prefix}/outlet_{i}/set" and payload in ["ON", "OFF"]:
            try:
                ibootbar.set_outlet(i, payload)
                state = ibootbar.get_outlet_state(i)
                client.publish(f"{mqtt_prefix}/outlet_{i}/state", state.upper(), retain=True)
            except Exception as e:
                print(f"Error controlling outlet {i}: {e}")
            break


def publish_states(client, userdata):
    ibootbar = userdata['ibootbar']
    mqtt_prefix = userdata['mqtt_prefix']
    try:
        states = ibootbar.get_all_outlets()
        for i in range(1, 9):
            state = states.get(i, {}).get("state", "OFF").upper()
            client.publish(f"{mqtt_prefix}/outlet_{i}/state", state, retain=True)
    except Exception as e:
        print("Failed to update states:", e)

    client.publish(f"{mqtt_prefix}/ip/state", get_local_ip(), retain=True)


def polling_thread(client, userdata):
    while True:
        publish_states(client, userdata)
        time.sleep(12)  # Update every 12 seconds


def undiscover(client, userdata):
    prefix = userdata['mqtt_prefix']
    for i in range(1, 9):
        client.publish(f"homeassistant/switch/{prefix}_outlet_{i}/config", "", retain=True)
    client.publish(f"homeassistant/sensor/{prefix}_ip/config", "", retain=True)
    client.publish(f"{prefix}/availability", "offline", retain=True)
    print("Undiscovery complete.")


def main():
    parser = argparse.ArgumentParser(description="iBootBar to Home Assistant via MQTT")
    parser.add_argument("--mqtt_host", required=True, help="MQTT broker IP")
    parser.add_argument("--mqtt_port", type=int, default=1883)
    parser.add_argument("--mqtt_user")
    parser.add_argument("--mqtt_pass")
    parser.add_argument("--serial_port", default="/dev/ttyUSB0")
    parser.add_argument("--mqtt_prefix", default="ibootbar")
    parser.add_argument("--debug", action="store_true", help="Show all serial traffic")
    parser.add_argument("--undiscover", action="store_true", help="Remove device from Home Assistant")
    args = parser.parse_args()

    ibootbar = IBootBar(port=args.serial_port, debug=args.debug)

    device_info = {
        "identifiers": [args.mqtt_prefix + "_device"],
        "name": "iBootBar Power Strip",
        "model": "iBoot-Bar",
        "manufacturer": "Dataprobe",
        "sw_version": "1.1"
    }

    userdata = {
        "ibootbar": ibootbar,
        "mqtt_prefix": args.mqtt_prefix,
        "device_info": device_info
    }

    client = mqtt.Client(userdata=userdata)
    if args.mqtt_user:
        client.username_pw_set(args.mqtt_user, args.mqtt_pass)
    client.will_set(f"{args.mqtt_prefix}/availability", "offline", retain=True)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(args.mqtt_host, args.mqtt_port, 60)

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
