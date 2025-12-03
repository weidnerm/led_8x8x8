#!/usr/bin/env python3

import serial
import re
import time
import argparse
import sys

class IBootBar:
    def __init__(self, port="/dev/ttyUSB0", baudrate=115200, timeout=1, debug=False):
        """
        Initialize the iBootBar controller.
        """
        
        self.debug = debug
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
            if self.debug:
                print('time.sleep(0.1)')
            time.sleep(0.1)
            # Wake up the device
            self.ser.write(b'\r\n')
            if self.debug:
                print('time.sleep(0.1)')
            time.sleep(0.1)
            self._read_response()  # Clear any garbage
        except serial.SerialException as e:
            print(f"Error opening serial port {port}: {e}")
            sys.exit(1)

    def _send_command(self, cmd):
        print('cmd:%s' % (cmd))
        self.ser.write((cmd + '\r\n').encode('utf-8'))
        if self.debug:
            print('time.sleep(0.15)')
        time.sleep(0.15)  # Critical: give device time to respond

    def _read_response(self):
        # ~ response = ""
        # ~ start_time = time.time()
        # ~ while time.time() - start_time < 0.5:
            # ~ if self.ser.in_waiting:
                # ~ line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                # ~ if line:
                    # ~ response += line + "\n"
                # ~ if 'OK' in response:
                    # ~ break
            # ~ else:
                # ~ print('time.sleep(0.05)')
                # ~ time.sleep(0.05)
                
        response = self.ser.read_until(b'SBB> ').decode('utf-8', errors='ignore').strip()
        print('response:%s' % (response))
      
        return response.strip()

    def _wait_for_prompt(self):
        """Sometimes the device is slow - wait for SBB> prompt"""
        self.ser.write(b'\r\n')
        if self.debug:
            print('time.sleep(0.2)')
        time.sleep(0.2)
        self._read_response()

    def set_outlet(self, number, state):
        if not 1 <= number <= 8:
            raise ValueError("Outlet number must be 1-8")
        state = state.capitalize()
        if state not in ["On", "Off"]:
            raise ValueError("State must be 'on' or 'off'")

        cmd = f"set outlet {number} {state.lower()}"
        max_retries = 10

        for attempt in range(max_retries):
            self._wait_for_prompt()
            self._send_command(cmd)
            print('cmd=%s' %(cmd))
            response = self._read_response()
            print('response=%s' %(response))

            if "OK" in response.upper():
                # Verify the actual state
                current = self.get_outlet_state(number)
                if current == state:
                    print(f"Outlet {number} successfully set to {state}")
                    return True
                else:
                    print(f"Verification failed: expected {state}, got {current} (attempt {attempt+1}/{max_retries})")
            else:
                print(f"Command failed (attempt {attempt+1}/{max_retries}): {response}")

            print('time.sleep(0.1)')
            time.sleep(0.1)

        raise Exception(f"Failed to set outlet {number} to {state} after {max_retries} attempts")

    def get_outlet_state(self, number):
        if not 1 <= number <= 8:
            raise ValueError("Outlet number must be 1-8")

        cmd = f"get outlet {number}"
        max_retries = 4

        for attempt in range(max_retries):
            self._wait_for_prompt()
            self._send_command(cmd)
            response = self._read_response()

            if "OK" in response.upper():
                match = re.search(r'(On|Off)', response, re.IGNORECASE)
                if match:
                    return match.group(1).capitalize()

            if self.debug:
                print('time.sleep(0.8)')
            time.sleep(0.8)

        raise Exception(f"Failed to read outlet {number}")

    def get_all_outlets(self):
        max_retries = 3
        for attempt in range(max_retries):
            self._wait_for_prompt()
            self._send_command("get outlets")
            response = self._read_response()

            if "OK" in response.upper() and "Outlet" in response:
                lines = [line.strip() for line in response.split('\n') if "Outlet" in line]
                result = {}
                for line in lines:
                    # Expected format: "1 Outlet1 Off" or similar
                    parts = line.split()
                    if len(parts) >= 3 and parts[0].isdigit():
                        num = int(parts[0])
                        state = parts[-1].capitalize()
                        name = " ".join(parts[1:-1])
                        result[num] = {"name": name, "state": state}
                if result:
                    return result
            if self.debug:
                print('time.sleep(1)')
            time.sleep(1)
        raise Exception("Failed to get all outlets")


def main():
    parser = argparse.ArgumentParser(description="Control Dataprobe iBoot-Bar via serial (Raspberry Pi)")
    parser.add_argument("-p", "--port", default="/dev/ttyUSB0", help="Serial port (default: /dev/ttyUSB0)")
    parser.add_argument("--debug", action="store_true", help="Show all outlets")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Set outlet
    set_parser = subparsers.add_parser("set", help="Set outlet state")
    set_parser.add_argument("outlet", type=int, choices=range(1,9), help="Outlet number 1-8")
    set_parser.add_argument("state", choices=["on", "off"], help="Desired state")

    # Get single outlet
    get_parser = subparsers.add_parser("get", help="Get outlet state")
    get_parser.add_argument("outlet", nargs="?", type=int, choices=range(1,9), help="Outlet number 1-8")
    get_parser.add_argument("--all", action="store_true", help="Show all outlets")

    args = parser.parse_args()

    iboot = IBootBar(port=args.port, debug=args.debug)

    try:
        if args.command == "set":
            iboot.set_outlet(args.outlet, args.state.capitalize())

        elif args.command == "get":
            if args.all:
                print("All outlets:")
                states = iboot.get_all_outlets()
                for num in sorted(states.keys()):
                    info = states[num]
                    print(f"  {num}: {info['name']:10} {info['state']}")
            elif args.outlet is not None:
                state = iboot.get_outlet_state(args.outlet)
                print(f"Outlet {args.outlet}: {state}")
            else:
                parser.error("get requires either an outlet number or --all")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        if iboot.ser.is_open:
            iboot.ser.close()


if __name__ == "__main__":
    main()
