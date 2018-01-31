#!/bin/sh

FIRMWARE="esp32-20180130-v1.9.3-240-ga275cb0f.bin"

sudo esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
sudo esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 "$FIRMWARE"

