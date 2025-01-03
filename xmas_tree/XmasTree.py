import time
import argparse
from rpi_ws281x import *
import os
import json
import socket
import sys
from Effects import Effects
from MqttLed import MqttLed
from threading import Lock
import traceback

class XmasTree:
    def __init__(self):
        self.effects = Effects('/home/pi/proj/led_8x8x8/xmas_tree/pre_made', self)
        self.mqtt = MqttLed(self)
        self.state = {
            'state':'OFF',
            'brightness':32,
            'color': {"r":255,"g":0,"b":0}
        }
        self.work_queue = []
        self.work_queue_lock = Lock()

    def process_state_command(self, command):
        # queue up the command to be worked on.
        self.work_queue_append(command)

    def work_queue_append(self, command):
        self.work_queue_lock.acquire()
        self.work_queue.append(command)
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
                # if 'effect' in command:
                #     self.state['effect'] = command['effect']
                
                self.state.pop('effect', None)  # drop the ongoing effect.


                # process command
                if 'effect' in command:
                    pass  # fixme.  handle effect
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

    myXmasTree = XmasTree()
    myXmasTree.mqtt.mqtt_connect()

    if args.undiscover:
        myXmasTree.mqtt.undiscover()
    else:
        myXmasTree.mqtt.discover()
        myXmasTree.mqtt.publish_ip()
        myXmasTree.effects.fill_full_cube_color(myXmasTree.state)
        myXmasTree.mqtt.send_state_update(myXmasTree.state)


        myXmasTree.run()



    myXmasTree.mqtt.mqtt_disconnect()

