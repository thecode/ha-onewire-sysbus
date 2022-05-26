"""Type definitions for 1-Wire integration."""
from __future__ import annotations

from dataclasses import dataclass

from pi1wire import OneWireInterface

from homeassistant.helpers.entity import DeviceInfo


@dataclass
class OWDeviceDescription:
    """1-Wire SysBus device description class."""

    device_info: DeviceInfo
    interface: OneWireInterface
