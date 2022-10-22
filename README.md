# Home Assistant 1-Wire via Sys Bus custom integration

**This is a spin-off from the original Home Assistant integration, which was removed in Home Assistant Core version 2022.6.**

**NOTE: This integration does not support connection via `owserver` [owfs 1-Wire file system](https://owfs.org/). For connection via `owserver`, use [Home Assistant 1-Wire integration](https://www.home-assistant.io/integrations/onewire/), both integrations can be used at the same time.**

The `onewire_sysbus` integration supports sensors which that using the One wire (1-wire) bus for communication.

Every 1-wire device has a (globally) unique ID that identifies the device on the bus. The first two digits identify a device family and the last 14 digits are a globally unique number given to it during manufacturing.

Different families have different functionality and can measure different quantities.

Each 1-wire component data sheet describes the different properties the component provides.

## Installation

### HACS

The recommend way to install `onewire_sysbus` is through [HACS](https://hacs.xyz/).
After installation restart Home Assistant and add the integration:
Navigate to **Settings** --> **Devices & Services** --> **ADD INTEGRATION** and select the `1-Wire SysBus` integration.

### Manual installation

Copy the `onewire_sysbus` folder and all of its contents into your Home Assistant's `custom_components` folder. This folder is usually inside your `/config` folder. If you are running Hass.io, use SAMBA to copy the folder over. You may need to create the `custom_components` folder and then copy the `onewire_sysbus` folder and all of its contents into it.
After installation restart Home Assistant and add the integration:
Navigate to **Settings** --> **Devices & Services** --> **ADD INTEGRATION** and select the `1-Wire SysBus` integration.

### Supported sensors

| Family | Device           | Physical Quantity  |
| -------|:-----|:-----|
| 10     | [DS18S20](https://www.maximintegrated.com/en/products/sensors/DS18S20.html)  | Temperature                     |
| 22     | [DS1822](https://datasheets.maximintegrated.com/en/ds/DS1822.pdf)            | Temperature                     |
| 28     | [DS18B20](https://datasheets.maximintegrated.com/en/ds/DS18B20.pdf)          | Temperature                     |
| 3B     | [DS1825](https://datasheets.maximintegrated.com/en/ds/DS1825.pdf)            | Temperature                     |
| 42     | [DS28EA00](https://datasheets.maximintegrated.com/en/ds/DS28EA00.pdf)        | Temperature                     |

## Interfacing with the 1-wire bus

The 1-Wire bus can be connected directly to the IO pins of Raspberry Pi or by using a dedicated interface adapter, for example
[DS9490R](https://datasheets.maximintegrated.com/en/ds/DS9490-DS9490R.pdf) or adapters based on [DS2482-100](https://datasheets.maximintegrated.com/en/ds/DS2482-100.pdf) that can be directly attached to the IO pins on the Raspberry Pi.

### Raspberry Pi set up

In order to setup 1-Wire support on Raspberry Pi, you'll need to edit `/boot/config.txt`. This file can not be edited through ssh. You have to put your SD card to a PC, and edit the file directly.
To edit `/boot/config.txt` on the Home Assistant Operating System, use [this documentation](https://developers.home-assistant.io/docs/operating-system/debugging.html) to enable SSH and edit `/mnt/boot/config.txt` via `vi`.

If you use an external pull-up resistor and the default GPIO 4 for the data line, add the following line:

```txt
dtoverlay=w1-gpio
```

If you don't want to use an external resistor, you can use a built-in one using the following line:

```txt
dtoverlay=w1-gpio-pullup
```

It is also possible to use a different GPIO pin like this to change it to pin 15:

```txt
dtoverlay=w1-gpio-pullup,gpiopin=15
```

Furthermore, it is also possible to have multiple GPIOs as one-wire data channel by adding multiple lines like this:

```txt
dtoverlay=w1-gpio-pullup,gpiopin=15
dtoverlay=w1-gpio-pullup,gpiopin=16
```

You can read about further parameters in this documentation: [Raspberry Pi Tutorial Series: 1-Wire DS18B20 Sensor](https://www.waveshare.com/wiki/Raspberry_Pi_Tutorial_Series:_1-Wire_DS18B20_Sensor#Enable_1-Wire).

When using the GPIO pins on Raspberry Pi directly as a 1-wire bus, the description above uses two kernel modules. `1w_gpio`, that implements the 1-wire protocol, and `1w_therm`, that understands the DS18B20 (family 28) components inner structure and reports temperature.
There is no support for other device types (families) and hence this onewire platform only supports temperature measurements from family 28 devices.

### Raspberry Pi checking connected devices via ssh

If you set up ssh, you can check the connected one-wire devices in the following folder: /sys/bus/w1/devices
The device IDs begin with `28-`.

### Entities

Upon startup of the platform, the 1-wire bus is searched for available 1-wire devices creates entities based on the sensor unique id:

`sensor.28.FF5C68521604_temperature`
