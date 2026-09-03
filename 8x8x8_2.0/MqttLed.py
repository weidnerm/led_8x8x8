import time
import paho.mqtt.client as mqtt
import netrc
import os
import json
import socket
import traceback

DISCOVER_REFRESH_SEC = 15 * 60
BROKER = 'homeassistant.local'


class MqttLed:
    def __init__(self, light):
        self.light = light

        self.dev_id           = 'led888rgb_ffe13e'
        self.dev_light_dev_id = 'led888rgb_ffe13e_lt'
        self.dev_sensor_ip_id = 'led888rgb_ffe13e_ip'

        self.command_topic      = 'cmnd/%s/state' % (self.dev_light_dev_id)
        self.state_topic        = 'stat/%s/state' % (self.dev_light_dev_id)
        self.ip_state_topic     = 'stat/%s/ipaddress' % (self.dev_sensor_ip_id)
        self.availability_topic = 'tele/%s/LWT' % (self.dev_id)

        self.last_discover_send_time = 0

    def discover(self):
        mqtt_discovery_payload_light = {
            'schema': 'json',
            'command_topic': self.command_topic,
            'state_topic': self.state_topic,
            'availability_topic': self.availability_topic,
            'payload_available': 'online',
            'payload_not_available': 'offline',
            'brightness': True,
            'supported_color_modes': ['rgb'],
            'effect': True,
            'effect_list': ['random_loop'] + self.light.effects.effect_name_list,
            'name': 'Light',
            'unique_id': self.dev_light_dev_id,
            'icon': 'mdi:cube-outline',
            'device': {
                'name': 'LED Cube 8x8x8 RGB',
                'identifiers': [self.dev_id],
                'mf': 'Michael Weidner',
                'model': 'RGB Cube Light',
                'sw': '2.01',
                'hw': '2.00',
            },
        }

        mqtt_discovery_payload_ip = {
            'name': 'ipaddress',
            'unique_id': self.dev_sensor_ip_id,
            'state_topic': self.ip_state_topic,
            'availability_topic': self.availability_topic,
            'payload_available': 'online',
            'payload_not_available': 'offline',
            'icon': 'mdi:ip-network',
            'device': {
                'name': 'LED Cube 8x8x8 RGB',
                'identifiers': [self.dev_id],
            },
        }

        self.last_discover_send_time = time.time()

        try:
            ret_config_1 = self.mqttc.publish(
                'homeassistant/light/%s/config' % (self.dev_light_dev_id),
                json.dumps(mqtt_discovery_payload_light),
                qos=1,
                retain=True,
            )
            ret_config_2 = self.mqttc.publish(
                'homeassistant/sensor/%s/config' % (self.dev_sensor_ip_id),
                json.dumps(mqtt_discovery_payload_ip),
                qos=1,
                retain=True,
            )
            ret_config_1.wait_for_publish()
            ret_config_2.wait_for_publish()
        except Exception:
            print(traceback.format_exc())

    def handle_discover_refresh(self):
        if time.time() > self.last_discover_send_time + DISCOVER_REFRESH_SEC:
            self.discover()
            self.send_state_update(self.light.state)

    def send_state_update(self, state):
        payload = dict(state)
        payload['color_mode'] = 'rgb'
        if not payload.get('effect'):
            payload.pop('effect', None)
        try:
            self.mqttc.publish(self.state_topic, json.dumps(payload), qos=0, retain=True)
        except Exception:
            print(traceback.format_exc())

    def undiscover(self):
        try:
            ret_config_1 = self.mqttc.publish(
                'homeassistant/light/%s/config' % (self.dev_light_dev_id), '', qos=1, retain=True)
            ret_config_2 = self.mqttc.publish(
                'homeassistant/sensor/%s/config' % (self.dev_sensor_ip_id), '', qos=1, retain=True)
            ret_config_1.wait_for_publish()
            ret_config_2.wait_for_publish()
        except Exception:
            print(traceback.format_exc())

    def read_netrc(self, filename=None):
        if filename is None:
            filename = os.path.expanduser('/home/pi/.netrc')
        try:
            auth = netrc.netrc(filename)
            hosts = {}
            for host in auth.hosts:
                hosts[host] = auth.authenticators(host)
            return hosts
        except netrc.NetrcParseError as e:
            print('Error parsing netrc file: %s' % (e,))
            return {}

    def get_credentials(self, machine):
        credentials = self.read_netrc()
        return credentials[machine]  # username, _, password

    def on_subscribe(self, client, userdata, mid, reason_code_list, properties):
        if reason_code_list and reason_code_list[0].is_failure:
            print('subscribe failed: %s' % (reason_code_list[0],))

    def on_message(self, client, userdata, message):
        if message.topic != self.command_topic:
            return
        try:
            update = json.loads(message.payload.decode('utf-8'))
        except Exception:
            print('decode error on payload %s' % (message.payload,))
            return
        print('command: %s' % (update,))
        self.light.process_state_command(update)

    def on_connect(self, client, userdata, flags, reason_code, properties):
        print('mqtt connected: %s' % (reason_code,))
        if reason_code.is_failure:
            print('Failed to connect: %s. loop will retry' % (reason_code,))
            return
        client.subscribe(self.command_topic)
        client.publish(self.availability_topic, 'online', qos=1, retain=True)
        self.send_state_update(self.light.state)
        self.publish_ip()

    def mqtt_connect(self):
        username, _, password = self.get_credentials(BROKER)
        self.mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqttc.username_pw_set(username=username, password=password)
        self.mqttc.will_set(self.availability_topic, 'offline', qos=1, retain=True)
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_message = self.on_message
        self.mqttc.on_subscribe = self.on_subscribe
        try:
            self.mqttc.connect(BROKER)
        except Exception:
            print(traceback.format_exc())
        self.mqttc.loop_start()

    def publish_ip(self):
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname + '.local')
        print('hostname = %s' % (hostname,))
        print('IPAddr = %s' % (IPAddr,))
        if IPAddr != '127.0.0.1':
            try:
                self.mqttc.publish(self.ip_state_topic, IPAddr, qos=1, retain=True)
            except Exception:
                print(traceback.format_exc())

    def mqtt_disconnect(self):
        try:
            self.mqttc.publish(self.availability_topic, 'offline', qos=1, retain=True)
            self.mqttc.disconnect()
            self.mqttc.loop_stop()
        except Exception:
            print(traceback.format_exc())
