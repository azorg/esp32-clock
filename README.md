# Micropython demo clock on ESP32
ESP32 with DHT22, DS18B22, DS3231 sensors and dot LED matrix on MAX7219

## Download Micropython firmware

Go to:

1. "Getting started with MicroPython on the ESP8266"
http://docs.micropython.org/en/latest/esp8266/esp8266/tutorial/intro.html

2. "Firmware for ESP32 boards"
look http://micropython.org/download

## Install `esptool.py` - ESP8266 & ESP32 ROM Bootloader Utility
```
$ sudo apt-get install python-pip
$ sudo pip install esptool
```
OR
```
$ sudo apt-get install python-serial
$ sudo apt-get install python-ecdsa ecdsautils
$ sudo apt-get install python-slowaes
$ git clone https://github.com/espressif/esptool.git
$ cd esptool
$ sudo python setup.py install
```

## Flash firmware on ESP8266 board
The following files are daily firmware for ESP32-based boards.
Program your board using the esptool.py program, and put the firmware
starting at address 0x1000

If you are putting MicroPython on for the first time then you should
first erase the entire flash. 

```
$ esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
$ esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 firmware.bin

```

## Build `mpy-cross`

```
$ sudo apt-get install build-essential libreadline-dev libffi-dev git
$ git clone --recurse-submodules https://github.com/micropython/micropython.git
$ cd ./micropython/ports/unix
$ make axtls
$ make
$ sudo cp ./micropython /usr/local/bin
```

## Install `ampy` - Utility to interact with a MicroPython board over a serial connection
```
$ sudo pip install adafruit-ampy
```
OR
```
$ sudo apt-get install python-click
$ git clone https://github.com/adafruit/ampy.git
$ cd ampy
$ sudo python setup.py install
```

## Compile python modules
```
$ mpy-cross main.py
$ mpy-cross ds3231.py
$ mpy-cross max7219.py
$ mpy-cross font_4x6.py
```

## Download files to ESP32 FLASH
```
$ ampy --port /dev/ttyUSB0 put main.py
$ ampy --port /dev/ttyUSB0 put ds3231.mpy
$ ampy --port /dev/ttyUSB0 put max7219.mpy
$ ampy --port /dev/ttyUSB0 put font_4x6.mpy
```

## Connect sensors and display to ESP32

Connect DTH22 to GND, 3.3V and GPIO-15

Connect DS18B20 to GND, 3.3V and GPIO-4

Connect DS3231 to GND, 3.3V, D21 (GPIO-21) to SDA and D22 (GPIO-22) to SCL

Connect MAX7219 to SPI:

| My ESP32   | ESP32         | max7219 8x8x4 LED Matrix |
| ---------- | ------------- | ------------------------ |
| 3V         | 3.3V          | VCC                      |
| GND        | GND           | GND                      |
| D14        | GPIO14 = SCK  | CLK                      |
| D12        | GPIO12 = MOSO | n/c                      |
| D13        | GPIO13 = MOSI | DIN                      |
| D27        | GPIO27        | CS (software)            |


## Run terminal (minicom, picocom or screen)
```
$ minicom -D /dev/ttyUSB0 -b 115200

$ picocom /dev/ttyUSB0 -b 115200

$ screen /dev/ttyUSB0 115200
```

## Set date/time in terminal
```
>>> rtc.set(datetime=(2017, 12, 31, 0, 23, 59, 00)
```

## Be happy!

