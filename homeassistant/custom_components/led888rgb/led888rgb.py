import asyncio
import aiohttp
import logging
import requests

# rest api based driver for controlling rgb 8x8x8 cube
LOGGER = logging.getLogger(__name__)

# async def discover():
#     """Discover Bluetooth LE devices."""
#     devices = await BleakScanner.discover()
#     LOGGER.debug("Discovered devices: %s", [{"address": device.address, "name": device.name} for device in devices])
#     return [device for device in devices if device.name.startswith("GDB5")]

class Led888rgbInstance:
    def __init__(self, ip_addr: str) -> None:
        self._ip_addr = ip_addr
        # self._device = BleakClient(self._mac)
        self._is_on = None
        # self._connected = None
        self._brightness = None
        self._rgb_color = None
        self._effect_list = None

    # async def _send(self, data: bytearray):
    #     LOGGER.debug(''.join(format(x, ' 03x') for x in data))
        
    #     if (not self._connected):
    #         await self.connect()
        
    #     crcinst = Crc8Maxim()
    #     crcinst.process(data)
    #     await self._device.write_gatt_char(WRITE_UUID, data + crcinst.finalbytes())

    @property
    def ip_addr(self):
        return self._ip_addr

    @property
    def is_on(self):
        return self._is_on

    @property
    def brightness(self):
        return self._brightness

    @property
    def rgb_color(self):
        return self._rgb_color

    # def set_brightness(self, intensity: int):
    async def set_brightness(self, intensity: int):
        # curl -X PATCH "http://192.168.86.70:5000/light/" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"brightness\": 16, \"rgb\": \"0000ff\", \"state\": \"on\"}"

        head = {"accept": "application/json", "Content-Type": "application/json"}
        url = "http://%s:5000/light/" % (self._ip_addr)
        payload = {
            "brightness": intensity
            }

        session = aiohttp.ClientSession()
        task = session.patch(url, json=payload, headers=head)
        responses = await asyncio.gather(task)
        r_json = None
        if len(responses) > 0:
            r_json = await responses[0].json()
        await session.close()

        self._brightness = intensity
        LOGGER.info("led888rgb setting brighness.  new state= %s" %(self._brightness))
        return r_json


    # def turn_on(self):
    async def turn_on(self):
        head = {"accept": "application/json", "Content-Type": "application/json"}
        url = "http://%s:5000/light/" % (self._ip_addr)
        payload = {"state": "on"}

        session = aiohttp.ClientSession()
        task = session.patch(url, json=payload, headers=head)
        responses = await asyncio.gather(task)
        r_json = None
        if len(responses) > 0:
            r_json = await responses[0].json()
        await session.close()
    
        self._is_on = True
        LOGGER.info("led888rgb turning on.  new state= %s" %(self._is_on))
        return r_json



    # def turn_off(self):
    async def turn_off(self):
        head = {"accept": "application/json", "Content-Type": "application/json"}
        url = "http://%s:5000/light/" % (self._ip_addr)
        payload = {"state": "off"}

        session = aiohttp.ClientSession()
        task = session.patch(url, json=payload, headers=head)
        responses = await asyncio.gather(task)
        r_json = None
        if len(responses) > 0:
            r_json = await responses[0].json()
        await session.close()

        self._is_on = False
        LOGGER.info("led888rgb turning off.  new state= %s" %(self._is_on))
        return r_json

    # def set_rgb_color(self, red_intensity: int, green_intensity: int, blue_intensity: int):
    async def set_rgb_color(self, red_intensity: int, green_intensity: int, blue_intensity: int):
        # curl -X PATCH "http://192.168.86.70:5000/light/" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"brightness\": 16, \"rgb\": \"0000ff\", \"state\": \"on\"}"

        head = {"accept": "application/json", "Content-Type": "application/json"}
        url = "http://%s:5000/light/" % (self._ip_addr)
        payload = {
            "rgb": '%02x%02x%02x' % (red_intensity, green_intensity, blue_intensity)
            }

        session = aiohttp.ClientSession()
        task = session.patch(url, json=payload, headers=head)
        responses = await asyncio.gather(task)
        r_json = None
        if len(responses) > 0:
            r_json = await responses[0].json()
        await session.close()

        self._rgb_color = (red_intensity, green_intensity, blue_intensity)

        return r_json

    async def set_effect(self, effect):
        head = {"accept": "application/json", "Content-Type": "application/json"}
        url = "http://%s:5000/light/" % (self._ip_addr)
        payload = {
            "effect": '%s' % (effect)
            }

        session = aiohttp.ClientSession()
        task = session.patch(url, json=payload, headers=head)
        responses = await asyncio.gather(task)
        r_json = None
        if len(responses) > 0:
            r_json = await responses[0].json()
        await session.close()

        self._effect = effect

        return r_json



    # async def connect(self):
    #     await self._device.connect(timeout=20)
    #     await asyncio.sleep(1)
    #     self._connected = True

    # async def disconnect(self):
    #     if self._device.is_connected:
    #         await self._device.disconnect()

    def get_effect_list(self):
        effect_list = self._effect_list
        if effect_list == None:
            effect_list = []
        return effect_list

    async def get_info(self):
        # curl -X GET "http://192.168.86.70:5000/light/" -H "accept: application/json"

        head = {"accept": "application/json"}
        url = "http://%s:5000/light/" % (self._ip_addr)

        session = aiohttp.ClientSession()
        task = session.get(url, headers=head)
        responses = await asyncio.gather(task)
        if len(responses) > 0:
            r_json = await responses[0].json()
        await session.close()

        LOGGER.info("led888rgb info is %s" %(r_json))



        if self._effect_list == None:
            # curl -X GET "http://192.168.86.70:5000/light/effect_list" -H "accept: application/json"

            head = {"accept": "application/json"}
            url = "http://%s:5000/light/effect_list" % (self._ip_addr)

            session = aiohttp.ClientSession()
            task = session.get(url, headers=head)
            responses = await asyncio.gather(task)
            if len(responses) > 0:
                r_json_2 = await responses[0].json()
                if 'effect_list' in r_json_2:
                    self._effect_list = r_json_2['effect_list']
                LOGGER.info("effect_list info is %s" %(r_json_2))
            await session.close()




        return r_json

        
# if __name__ == '__main__':
#     myLed888rgbInstance = Led888rgbInstance(ip_addr='192.168.86.70')
#     myLed888rgbInstance.turn_on()
#     time.sleep(1)
#     myLed888rgbInstance.set_rgb_color(255,0,0)
#     myLed888rgbInstance.set_brightness(1)
#     time.sleep(1)
#     myLed888rgbInstance.set_rgb_color(0,255,0)
#     myLed888rgbInstance.set_brightness(2)
#     time.sleep(1)
#     myLed888rgbInstance.set_rgb_color(0,0,255)
#     myLed888rgbInstance.set_brightness(4)
#     time.sleep(1)
#     myLed888rgbInstance.set_brightness(8)
#     time.sleep(1)
#     myLed888rgbInstance.set_brightness(16)
#     time.sleep(1)
#     myLed888rgbInstance.set_brightness(32)
#     time.sleep(1)
#     myLed888rgbInstance.set_brightness(64)
#     time.sleep(1)
#     myLed888rgbInstance.set_brightness(16)
#     time.sleep(1)
#     myLed888rgbInstance.turn_off()


