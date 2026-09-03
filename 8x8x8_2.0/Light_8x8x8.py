import time
import argparse
from rpi_ws281x import *
import os
import json
import socket
import sys
from Effects import Effects
from MqttLed import MqttLed
from TextWrap import normalize_text, USER_WRAP_FILE
from threading import Lock
import traceback

WRAP_TEXT_PATH = '/home/pi/proj/led_8x8x8/8x8x8_2.0/wrap_text.txt'
DEFAULT_WRAP_TEXT = 'HELLO'


class Light_8x8x8:
    def __init__(self):
        self.wrap_text = self._load_wrap_text()
        self.effects = Effects('/home/pi/proj/led_8x8x8/8x8x8/pre_made/', self)
        self.mqtt = MqttLed(self)
        self.state = {
            'state':'OFF',
            'brightness':32,
            'color': {"r":255,"g":192,"b":140}
        }
        self.work_queue = []
        self.work_queue_lock = Lock()
        self.effects.generate_user_wrap_seq(self.wrap_text)

    def _load_wrap_text(self):
        try:
            with open(WRAP_TEXT_PATH, 'r') as fh:
                text = fh.read()
            return normalize_text(text) or DEFAULT_WRAP_TEXT
        except Exception:
            return DEFAULT_WRAP_TEXT

    def set_wrap_text(self, text):
        text = normalize_text(text) or DEFAULT_WRAP_TEXT
        self.wrap_text = text
        try:
            tmp = WRAP_TEXT_PATH + '.tmp'
            with open(tmp, 'w') as fh:
                fh.write(text)
            os.replace(tmp, WRAP_TEXT_PATH)
        except Exception:
            print(traceback.format_exc())
        self.effects.generate_user_wrap_seq(text)
        self.mqtt.send_text_update(text)

    def process_state_command(self, command):
        # queue up the command to be worked on.
        self.work_queue_append(command)

    def work_queue_append(self, command):
        # Latest MQTT command wins. Drop stale commands so an aborted
        # effect does not replay an older color/effect afterwards.
        self.work_queue_lock.acquire()
        self.work_queue = [command]
        self.work_queue_lock.release()

    def work_queue_pop(self):
        command = None

        self.work_queue_lock.acquire()
        if len(self.work_queue) > 0:
            command = self.work_queue.pop()
        self.work_queue_lock.release()

        return command
    
    def get_work_queue_length(self):
        self.work_queue_lock.acquire()
        length = len(self.work_queue)
        self.work_queue_lock.release()

        return length

    def run(self):
        while True:
            # get command from work queue.  do it safely
            command = self.work_queue_pop()

            if command != None:
                # update our tracking
                if 'state' in command:
                    self.state['state'] = command['state']
                if 'brightness' in command:
                    self.state['brightness'] = command['brightness']
                if 'color' in command:
                    self.state['color'] = command['color']

                self.state.pop('effect', None)  # drop the ongoing effect.

                # process command
                if 'effect' in command:
                    self.effects.play_effect(command['effect'])
                else:
                    self.mqtt.send_state_update(self.state)
                    self.effects.fill_full_cube_color(self.state)

            self.mqtt.handle_discover_refresh()  # occasionally resend the discovery message
            time.sleep(0.005)


# Main program logic follows:
if __name__ == '__main__':

    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-ud', '--undiscover', action='store_true', help='undiscover from homeassistant MQTT')
    args = parser.parse_args()

    myLight_8x8x8 = Light_8x8x8()
    myLight_8x8x8.mqtt.mqtt_connect()

    if args.undiscover:
        myLight_8x8x8.mqtt.undiscover()
    else:
        myLight_8x8x8.mqtt.discover()
        myLight_8x8x8.mqtt.publish_ip()
        myLight_8x8x8.mqtt.send_text_update(myLight_8x8x8.wrap_text)
        myLight_8x8x8.effects.fill_full_cube_color(myLight_8x8x8.state)
        myLight_8x8x8.mqtt.send_state_update(myLight_8x8x8.state)


        myLight_8x8x8.run()



    myLight_8x8x8.mqtt.mqtt_disconnect()
