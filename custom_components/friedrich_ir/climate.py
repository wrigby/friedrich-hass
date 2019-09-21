import logging

from typing import List

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.components.climate import (
    ClimateDevice,
    PLATFORM_SCHEMA,
    SUPPORT_FAN_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)

from homeassistant.components.climate.const import (
    HVAC_MODE_OFF,
    HVAC_MODE_AUTO,
    HVAC_MODE_COOL,
    HVAC_MODE_DRY,
    HVAC_MODE_FAN_ONLY,
)

from homeassistant.const import (
    CONF_NAME,
    TEMP_FAHRENHEIT,
)

MIN_TEMP = 59
MAX_TEMP = 91

CONF_DEVICE = "device"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_DEVICE, default="/dev/ttyACM0"): cv.string,
    vol.Required(CONF_NAME, default="Air Conditioner"): cv.string,
})


_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None):
    tty_dev = config[CONF_DEVICE]
    name = config[CONF_NAME]
    add_entities([FriedrichIR(name, tty_dev)])


class FriedrichIR(ClimateDevice):

    _fan_mode_map = {
        "Low": 1,
        "Medium": 2,
        "High": 3,
    }

    _mode_map = {
        HVAC_MODE_OFF: None,
        HVAC_MODE_AUTO: "M",
        HVAC_MODE_COOL: "C",
        HVAC_MODE_DRY: "D",
        HVAC_MODE_FAN_ONLY: "F",
    }

    def __init__(self, name, dev):
        _LOGGER.info("Friedrich IR configured at %s", dev)
        self._name = name
        self._dev = dev
        self._temp = 72
        self._mode = HVAC_MODE_COOL
        self._fan_mode = "High"
        self._send_update()

    @property
    def name(self) -> str:
        return self._name

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return SUPPORT_TARGET_TEMPERATURE | SUPPORT_FAN_MODE

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        return MIN_TEMP

    @property
    def max_temp(self) -> float:
        """Return the minimum temperature."""
        return MAX_TEMP
    
    @property
    def fan_modes(self) -> List[str]:
        return list(self._fan_mode_map.keys())

    @property
    def temperature_unit(self) -> str:
        return TEMP_FAHRENHEIT

    @property
    def target_temperature(self) -> float:
        return self._temp

    @property
    def hvac_modes(self) -> List[str]:
        return list(self._mode_map.keys())

    @property
    def hvac_mode(self) -> str:
        return self._mode

    @property
    def fan_mode(self) -> str:
        return self._fan_mode

    def set_fan_mode(self, fan_mode):
        self._fan_mode = fan_mode
        self._send_update()

    def set_hvac_mode(self, mode):
        self._mode = mode
        self._send_update()

    def set_temperature(self, **kwargs):
        self._temp = kwargs["temperature"]
        self._send_update()

    def _send_update(self):
        """ Build and send a full command """
        fan_speed = self._fan_mode_map[self._fan_mode]
        mode = self._mode_map[self._mode]
        temp = int(self._temp)
        cmd = f"$PAC,1,{mode},{temp},{fan_speed}\n"
        _LOGGER.info("Sending command %s", cmd.strip())
        with open(self._dev, "w") as f:
            f.write(cmd)

