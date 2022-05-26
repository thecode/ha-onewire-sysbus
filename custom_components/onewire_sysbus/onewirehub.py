"""Hub for communication with 1-Wire mount_dir via SysBus."""
from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from pi1wire import Pi1Wire

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_IDENTIFIERS,
    ATTR_MANUFACTURER,
    ATTR_MODEL,
    ATTR_NAME,
    ATTR_VIA_DEVICE,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity import DeviceInfo

from .const import (
    CONF_MOUNT_DIR,
    DEVICE_SUPPORT_SYSBUS,
    DOMAIN,
    MANUFACTURER_EDS,
    MANUFACTURER_HOBBYBOARDS,
    MANUFACTURER_MAXIM,
)
from .model import OWDeviceDescription

DEVICE_MANUFACTURER = {
    "7E": MANUFACTURER_EDS,
    "EF": MANUFACTURER_HOBBYBOARDS,
}

_LOGGER = logging.getLogger(__name__)


class OneWireHub:
    """Hub to communicate with SysBus or OWServer."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize."""
        self.hass = hass
        self.pi1proxy: Pi1Wire | None = None
        self.devices: list[OWDeviceDescription] | None = None

    async def check_mount_dir(self, mount_dir: str) -> None:
        """Test that the mount_dir is a valid path."""
        if not await self.hass.async_add_executor_job(os.path.isdir, mount_dir):
            raise InvalidPath
        self.pi1proxy = Pi1Wire(mount_dir)

    async def initialize(self, config_entry: ConfigEntry) -> None:
        """Initialize a config entry."""
        mount_dir = config_entry.data[CONF_MOUNT_DIR]
        await self.check_mount_dir(mount_dir)
        await self.discover_devices()

        if TYPE_CHECKING:
            assert self.devices
        # Register discovered devices on Hub
        device_registry = dr.async_get(self.hass)
        for device in self.devices:
            device_info: DeviceInfo = device.device_info
            device_registry.async_get_or_create(
                config_entry_id=config_entry.entry_id,
                identifiers=device_info[ATTR_IDENTIFIERS],
                manufacturer=device_info[ATTR_MANUFACTURER],
                model=device_info[ATTR_MODEL],
                name=device_info[ATTR_NAME],
                via_device=device_info.get(ATTR_VIA_DEVICE),
            )

    async def discover_devices(self) -> None:
        """Discover all devices."""
        if self.devices is None:
            self.devices = await self.hass.async_add_executor_job(
                self._discover_devices_sysbus
            )

    def _discover_devices_sysbus(self) -> list[OWDeviceDescription]:
        """Discover all sysbus devices."""
        devices: list[OWDeviceDescription] = []
        assert self.pi1proxy
        all_sensors = self.pi1proxy.find_all_sensors()
        if not all_sensors:
            _LOGGER.error(
                "No onewire sensor found. Check if dtoverlay=w1-gpio "
                "is in your /boot/config.txt. "
                "Check the mount_dir parameter if it's defined"
            )
        for interface in all_sensors:
            device_family = interface.mac_address[:2]
            device_id = f"{device_family}-{interface.mac_address[2:]}"
            if device_family not in DEVICE_SUPPORT_SYSBUS:
                _LOGGER.warning(
                    "Ignoring unknown device family (%s) found for device %s",
                    device_family,
                    device_id,
                )
                continue
            device_info: DeviceInfo = {
                ATTR_IDENTIFIERS: {(DOMAIN, device_id)},
                ATTR_MANUFACTURER: DEVICE_MANUFACTURER.get(
                    device_family, MANUFACTURER_MAXIM
                ),
                ATTR_MODEL: device_family,
                ATTR_NAME: device_id,
            }
            device = OWDeviceDescription(
                device_info=device_info,
                interface=interface,
            )
            devices.append(device)
        return devices


class InvalidPath(HomeAssistantError):
    """Error to indicate the path is invalid."""
