"""Support for 1-Wire environment sensors."""
from __future__ import annotations

import asyncio
from collections.abc import Callable, Mapping
from dataclasses import dataclass
import logging
from typing import Any

from pi1wire import InvalidCRCException, OneWireInterface, UnsupportResponseException

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import DOMAIN, READ_MODE_FLOAT
from .model import OWDeviceDescription
from .onewire_entities import OneWireEntity, OneWireEntityDescription
from .onewirehub import OneWireHub


@dataclass
class OneWireSensorEntityDescription(OneWireEntityDescription, SensorEntityDescription):
    """Class describing OneWire sensor entities."""

    override_key: Callable[[str, Mapping[str, Any]], str] | None = None


SIMPLE_TEMPERATURE_SENSOR_DESCRIPTION = OneWireSensorEntityDescription(
    key="temperature",
    device_class=SensorDeviceClass.TEMPERATURE,
    name="Temperature",
    native_unit_of_measurement=TEMP_CELSIUS,
    read_mode=READ_MODE_FLOAT,
    state_class=SensorStateClass.MEASUREMENT,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up 1-Wire platform."""
    onewirehub = hass.data[DOMAIN][config_entry.entry_id]
    entities = await hass.async_add_executor_job(get_entities, onewirehub)
    async_add_entities(entities, True)


def get_entities(onewirehub: OneWireHub) -> list[SensorEntity]:
    """Get a list of entities."""
    if not onewirehub.devices:
        return []

    entities: list[SensorEntity] = []

    for device in onewirehub.devices:
        assert isinstance(device, OWDeviceDescription)
        p1sensor: OneWireInterface = device.interface
        family = p1sensor.mac_address[:2]
        device_id = f"{family}-{p1sensor.mac_address[2:]}"
        device_info = device.device_info
        description = SIMPLE_TEMPERATURE_SENSOR_DESCRIPTION
        device_file = f"/sys/bus/w1/devices/{device_id}/w1_slave"
        name = f"{device_id} {description.name}"
        entities.append(
            OneWireSensor(
                description=description,
                device_id=device_id,
                device_file=device_file,
                device_info=device_info,
                name=name,
                owsensor=p1sensor,
            )
        )

    return entities


class OneWireSensor(OneWireEntity, SensorEntity):
    """Implementation of a 1-Wire sensor directly connected to RPI GPIO."""

    entity_description: OneWireSensorEntityDescription

    def __init__(
        self,
        description: OneWireSensorEntityDescription,
        device_id: str,
        device_info: DeviceInfo,
        device_file: str,
        name: str,
        owsensor: OneWireInterface,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            description=description,
            device_id=device_id,
            device_info=device_info,
            device_file=device_file,
            name=name,
        )
        self._attr_unique_id = device_file
        self._owsensor = owsensor

    @property
    def native_value(self) -> StateType:
        """Return the state of the entity."""
        return self._state

    async def get_temperature(self) -> float:
        """Get the latest data from the device."""
        attempts = 1
        while True:
            try:
                return await self.hass.async_add_executor_job(
                    self._owsensor.get_temperature
                )
            except UnsupportResponseException as ex:
                _LOGGER.debug(
                    "Cannot read from sensor %s (retry attempt %s): %s",
                    self._device_file,
                    attempts,
                    ex,
                )
                await asyncio.sleep(0.2)
                attempts += 1
                if attempts > 10:
                    raise

    async def async_update(self) -> None:
        """Get the latest data from the device."""
        try:
            self._value_raw = await self.get_temperature()
            self._state = round(self._value_raw, 1)
        except (
            FileNotFoundError,
            InvalidCRCException,
            UnsupportResponseException,
        ) as ex:
            _LOGGER.warning(
                "Cannot read from sensor %s: %s",
                self._device_file,
                ex,
            )
            self._state = None
