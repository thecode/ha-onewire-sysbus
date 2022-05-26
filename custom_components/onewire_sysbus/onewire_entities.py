"""Support for 1-Wire entities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.helpers.entity import DeviceInfo, Entity, EntityDescription
from homeassistant.helpers.typing import StateType


@dataclass
class OneWireEntityDescription(EntityDescription):
    """Class describing OneWire entities."""

    read_mode: str | None = None


class OneWireEntity(Entity):
    """Implementation of a 1-Wire entity."""

    entity_description: OneWireEntityDescription

    def __init__(
        self,
        description: OneWireEntityDescription,
        device_id: str,
        device_info: DeviceInfo,
        device_file: str,
        name: str,
    ) -> None:
        """Initialize the entity."""
        self.entity_description = description
        self._attr_unique_id = f"/{device_id}/{description.key}"
        self._attr_device_info = device_info
        self._attr_name = name
        self._device_file = device_file
        self._state: StateType = None
        self._value_raw: float | None = None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return the state attributes of the entity."""
        return {
            "device_file": self._device_file,
            "raw_value": self._value_raw,
        }
