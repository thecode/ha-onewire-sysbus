"""Constants for 1-Wire component."""
from __future__ import annotations

from homeassistant.const import Platform

CONF_MOUNT_DIR = "mount_dir"
DEFAULT_SYSBUS_MOUNT_DIR = "/sys/bus/w1/devices/"

DOMAIN = "onewire_sysbus"

DEVICE_SUPPORT_SYSBUS = ["10", "22", "28", "3B", "42"]

MANUFACTURER_MAXIM = "Maxim Integrated"
MANUFACTURER_HOBBYBOARDS = "Hobby Boards"
MANUFACTURER_EDS = "Embedded Data Systems"

READ_MODE_FLOAT = "float"

PLATFORMS = [Platform.SENSOR]
