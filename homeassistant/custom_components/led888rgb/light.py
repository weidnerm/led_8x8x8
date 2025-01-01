"""Platform for light integration."""
from __future__ import annotations

import logging

from .led888rgb import Led888rgbInstance
import voluptuous as vol

from pprint import pformat

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (SUPPORT_BRIGHTNESS, 
                                            ATTR_BRIGHTNESS,
                                            ATTR_RGB_COLOR,
                                            ATTR_EFFECT,
                                            PLATFORM_SCHEMA, 
                                            EFFECT_OFF, 
                                            LightEntity,
                                            LightEntityFeature,
                                            ColorMode)
from homeassistant.const import CONF_NAME, CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME): cv.string,
    vol.Required(CONF_HOST): cv.string,
})


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the LED 888 RGB Cube Light."""
    # Add devices
    _LOGGER.info(pformat(config))
    
    light = {
        "name": config[CONF_NAME],
        "host": config[CONF_HOST]
    }
    
    add_entities([Led88rgbLight(light)])

class Led88rgbLight(LightEntity):
    """Representation of an LED888 Light."""

    def __init__(self, light) -> None:
        """Initialize an Led88rgbLight."""
        _LOGGER.info(pformat(light))
        self._name = light["name"]
        # self._name = "fixme name"
        self._light = Led888rgbInstance(light["host"])
        self._state = None
        self._brightness = None
        self._effect = EFFECT_OFF
        self._effect_list = ['random_loop', 'drum_1']

    @property
    def icon(self) -> str | None:
        """Icon of the entity."""
        return "mdi:cube-outline"

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Return the brightness of the light.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness

    @property
    def supported_features(self):
        return LightEntityFeature.EFFECT

    @property
    def color_mode(self):
        return ColorMode.RGB

    @property
    def supported_color_modes(self):
        return {ColorMode.RGB}

    @property
    def effect_list(self):
        return self._effect_list

    @property
    def effect(self):
        return self._effect



    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        
        if ATTR_RGB_COLOR  in kwargs:
            # _LOGGER.debug('ATTR_RGB_COLOR %s' % (kwargs.get(ATTR_RGB_COLOR, 'ff0000')))
            rgb_color = kwargs.get(ATTR_RGB_COLOR, [0xff,00,00])
            await self._light.set_rgb_color(rgb_color[0], rgb_color[1], rgb_color[2])

        if ATTR_BRIGHTNESS in kwargs:
            await self._light.set_brightness(kwargs.get(ATTR_BRIGHTNESS, 255))
            
        if ATTR_EFFECT in kwargs:
            effect = kwargs.get(ATTR_EFFECT, '')
            await self._light.set_effect(effect)
            self._effect = effect
        else:
            self._effect = EFFECT_OFF

        if ATTR_EFFECT not in kwargs: # only turn on if no effect
            r_json = await self._light.turn_on()
            self.parse_state(r_json)
        _LOGGER.debug('async_turn_on kwargs %s' % (kwargs))


    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        r_json = await self._light.turn_off()
        self.parse_state(r_json)

    async def async_update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        r_json = await self._light.get_info()
        self.parse_state(r_json)
        self._effect_list = self._light.get_effect_list()



    def parse_state(self, r_json):

        if r_json:
            if r_json['state'] == 'on':
                self._state = True
            else:
                self._state = False

            self._brightness = r_json['brightness']

            red_intensity = int(r_json['rgb'][0:2], 16)
            green_intensity = int(r_json['rgb'][2:4], 16)
            blue_intensity = int(r_json['rgb'][4:6], 16)
            self._rgb_color = (red_intensity, green_intensity, blue_intensity)

