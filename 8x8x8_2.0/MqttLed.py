import time
import argparse
import paho.mqtt.client as mqtt
import netrc
import os
import json
import socket
import sys
import traceback

class MqttLed:
    def __init__(self, light):
        self.light = light

        self.dev_id           = 'led888rgb_ffe13e'
        self.dev_light_dev_id = 'led888rgb_ffe13e_lt'
        self.dev_sensor_ip_id = 'led888rgb_ffe13e_ip'


        self.brightness_command_topic = 'cmnd/%s/brightness' % (self.dev_light_dev_id)
        self.brightness_state_topic   = 'stat/%s/brightness' % (self.dev_light_dev_id)

        self.command_topic            = 'cmnd/%s/state' % (self.dev_light_dev_id)
        self.state_topic              = 'stat/%s/state' % (self.dev_light_dev_id)

        self.rgb_command_topic        = 'cmnd/%s/rgb' % (self.dev_light_dev_id)
        self.rgb_state_topic          = 'stat/%s/rgb' % (self.dev_light_dev_id)

        self.effect_command_topic     = 'cmnd/%s/effect' % (self.dev_light_dev_id)
        self.effect_state_topic       = 'stat/%s/effect' % (self.dev_light_dev_id)
        
        self.ip_state_topic           = "stat/%s/ipaddress" % (self.dev_sensor_ip_id)

        self.last_discover_send_time = time.time()
        # >>> from uuid import getnode as get_mac
        # >>> mac = get_mac()
        # >>> print(mac)
        # 202481602650430
        # >>> print('%x' % mac)
        # b827ebffe13e
        # >>> 

    def discover(self):
        mqtt_discovery_payload_light = {
            # 'brightness_command_topic' : self.brightness_command_topic,
            # 'brightness_state_topic'   : self.brightness_state_topic,

            'command_topic'            : self.command_topic,
            'state_topic'              : self.state_topic,

            # 'rgb_command_topic'        : self.rgb_command_topic,
            # 'rgb_state_topic'          : self.rgb_state_topic,

            # 'effect_command_topic'     : self.effect_command_topic,
            # 'effect_state_topic'       : self.effect_state_topic,

            # 'state_value_template'     : '{{ value_json.state }}',
            # 'effect_value_template'    : '{{ value_json.effect }}',
            # 'brightness_value_template': '{{ value_json.brightness }}',
            # 'rgb_value_template'       : "{{ value_json.rgb | join(',') }}",

            'platform': 'light',
            'schema': 'json',
            'supported_color_modes': ['rgb'],  # 'onoff' or 'brightness', 'rgb'
            'effect': True,
            'effect_list' : ['random_loop'] + self.light.effects.effect_name_list,
            "name": "Light",
            "unique_id": self.dev_light_dev_id,
            "icon": "mdi:cube-outline",
            "device": {
                "name": "LED Cube 8x8x8 RGB",
                "identifiers": self.dev_id,
                "mf": "Michael Weidner",
                "model": "RGB Cube Light",
                "sw": "2.00",
                "hw": "2.00",
                }
        }
        to_add = {
            'brightness_command_template': 'fixme',
            'color_mode_state_topic' : 'fixme',
            'color_mode_value_template' : 'fixme',
            'effect_command_template'  : 'fixme',
            'rgb_command_template'   : 'fixme',
        }

        mqtt_discovery_payload_ip = {
            "name": "ipaddress",
            "unique_id": self.dev_sensor_ip_id,
            "state_topic": self.ip_state_topic,
            "icon": "mdi:ip-network",
            "device": {
                "name": "LED Cube 8x8x8 RGB",
                "identifiers": self.dev_id,
                }
        }


        self.last_discover_send_time = time.time()
        
        try:
            ret_config_1 = self.mqttc.publish("homeassistant/light/%s/config" % (self.dev_light_dev_id), json.dumps(mqtt_discovery_payload_light), True)
            ret_config_2 = self.mqttc.publish("homeassistant/sensor/%s/config" % (self.dev_sensor_ip_id), json.dumps(mqtt_discovery_payload_ip), True)
        
            ret_config_1.wait_for_publish()
            ret_config_2.wait_for_publish()
        except:
            exception_text = traceback.format_exc()
            print(exception_text)

    def handle_discover_refresh(self):
        if time.time() > self.last_discover_send_time + 1*60:
            self.discover()
            self.send_state_update(self.light.state)


    def send_state_update(self, state):
        
        try:
            ret_state_2 = self.mqttc.publish(self.state_topic, json.dumps(state), False)
        except:
            exception_text = traceback.format_exc()
            print(exception_text)


    def undiscover(self):
        try:
            ret_config_1 = self.mqttc.publish("homeassistant/light/%s/config" % (self.dev_light_dev_id), '', True)
            ret_config_2 = self.mqttc.publish("homeassistant/sensor/%s/config" % (self.dev_sensor_ip_id), '', True)

            ret_config_1.wait_for_publish()
            ret_config_2.wait_for_publish()
        except:
            exception_text = traceback.format_exc()
            print(exception_text)



    def read_netrc(self, filename=None):
        """Reads a .netrc file and returns a dictionary of hosts and their credentials."""
        if filename is None:
            filename = os.path.expanduser("/home/pi/.netrc")

        try:
            auth = netrc.netrc(filename)
            hosts = {}
            for host in auth.hosts:
                hosts[host] = auth.authenticators(host)
            return hosts
        except netrc.NetrcParseError as e:
            print(f"Error parsing netrc file: {e}")
            return {}


    def get_credentials(self, machine):
        credentials = self.read_netrc()
        if machine in credentials:
            print(credentials)
        return credentials[machine] # username, _ , password
        

        
    def on_subscribe(self, client, userdata, mid, reason_code_list, properties):
        print('on_subscribe reached')
        # Since we subscribed only for a single channel, reason_code_list contains
        # a single entry
        if reason_code_list[0].is_failure:
            print(f"Broker rejected you subscription: {reason_code_list[0]}")
        else:
            print(f"Broker granted the following QoS: {reason_code_list[0].value}")

    def on_unsubscribe(self, client, userdata, mid, reason_code_list, properties):
        print('on_unsubscribe reached')
        # Be careful, the reason_code_list is only present in MQTTv5.
        # In MQTTv3 it will always be empty
        if len(reason_code_list) == 0 or not reason_code_list[0].is_failure:
            print("unsubscribe succeeded (if SUBACK is received in MQTTv3 it success)")
        else:
            print(f"Broker replied with failure: {reason_code_list[0]}")
        # ~ client.disconnect()

    def on_message(self, client, userdata, message):
        print('on_message reached   topic=%s  message=%s' % (message.topic, message.payload))
        # userdata is the structure we choose to provide, here it's a list()
        userdata.append(message.payload)
        # We only want to process 10 messages
        if len(userdata) >= 40:
            client.unsubscribe("$SYS/#")

        if message.topic == self.command_topic:
            try:
                update = json.loads(message.payload.decode('utf-8'))
            except:
                print('decode error on payload %s' % message.payload)
            self.light.process_state_command(update)

    def on_connect(self, client, userdata, flags, reason_code, properties):
        print('on_connect reached.  flags=%s  reason_code=%s  properties=%s' % (flags, reason_code, properties))
        if reason_code.is_failure:
            print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
        else:
            # we should always subscribe from on_connect callback to be sure
            # our subscribed is persisted across reconnections.
            client.subscribe("$SYS/#")
            self.mqttc.subscribe(self.command_topic)
            self.mqttc.subscribe(self.effect_command_topic)
            self.send_state_update(self.light.state)
            self.publish_ip()

    def on_publish(self, client, userdata, mid, reason_code, properties):
        # reason_code and properties will only be present in MQTTv5. It's always unset in MQTTv3
        print('on_publish reached.  mid=%s  reason_code=%s  properties=%s' % (mid, reason_code, properties))
        # ~ try:
            # ~ userdata.remove(mid)
        # ~ except KeyError:
            # ~ print("on_publish() is called with a mid not present in unacked_publish")
            # ~ print("This is due to an unavoidable race-condition:")
            # ~ print("* publish() return the mid of the message sent.")
            # ~ print("* mid from publish() is added to unacked_publish by the main thread")
            # ~ print("* on_publish() is called by the loop_start thread")
            # ~ print("While unlikely (because on_publish() will be called after a network round-trip),")
            # ~ print(" this is a race-condition that COULD happen")
            # ~ print("")
            # ~ print("The best solution to avoid race-condition is using the msg_info from publish()")
            # ~ print("We could also try using a list of acknowledged mid rather than removing from pending list,")
            # ~ print("but remember that mid could be re-used !")




    def mqtt_connect(self):
        username, _, password = self.get_credentials('homeassistant.local')
        # connect to MQTT Broker and set callback for incoming messages
        self.mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqttc.username_pw_set(username=username, password=password)
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_message = self.on_message
        self.mqttc.on_subscribe = self.on_subscribe
        self.mqttc.on_unsubscribe = self.on_unsubscribe
        self.mqttc.on_publish = self.on_publish

        self.mqttc.user_data_set([])
        try:
            self.mqttc.connect("homeassistant.local")
        except:
            exception_text = traceback.format_exc()
            print(exception_text)

        # ~ # subscribe to topics

        
        self.mqttc.loop_start()


    # def not_yet(self):
        

        
    #     # publish a message
    #     ret_config_2 = None
    #     if disconnect == True:
    #         ret_config_1 = self.mqttc.publish("homeassistant/sensor/moonfoot001_1/config", '', True)
    #         ret_config_2 = self.mqttc.publish("homeassistant/sensor/moonfoot001_2/config", '', True)
    #     else:
    #         ret_config_1 = self.mqttc.publish("homeassistant/sensor/moonfoot001_1/config", json.dumps(mqtt_discovery_payload_light), True)
    #         ret_config_2 = self.mqttc.publish("homeassistant/sensor/moonfoot001_2/config", json.dumps(mqtt_discovery_payload_ip), True)
        
    #     time.sleep(1)

    #     # ~ self.mqttc.loop_forever()
    #     print(f"Received the following message: {self.mqttc.user_data_get()}")

    #     ret_config_1.wait_for_publish()
    #     if ret_config_2:
    #         ret_config_2.wait_for_publish()


    #     ret_state_1 = self.mqttc.publish("stat/moonfoot001/state", state, True)
    #     ret_state_1.wait_for_publish()

    def publish_ip(self):
        hostname = socket.gethostname() # get our hostname
        IPAddr = socket.gethostbyname(hostname+'.local')
        print('hostname = %s' % (hostname))
        print('IPAddr = %s' % (IPAddr))
        if IPAddr != '127.0.0.1': #do a sanity check since it doesnt always work.  not sure why
            try:
                ret_state_2 = self.mqttc.publish(self.ip_state_topic, IPAddr, True)

                # ret_state_2.wait_for_publish()
            except:
                exception_text = traceback.format_exc()
                print(exception_text)


    def mqtt_disconnect(self):

        try:
            self.mqttc.disconnect()
            self.mqttc.loop_stop()
        except:
            exception_text = traceback.format_exc()
            print(exception_text)

    def start(self):
        time.sleep(30)


  
# Main program logic follows:
if __name__ == '__main__':
    myMqttLed = MqttLed()



