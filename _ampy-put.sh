#!/bin/sh

if mpy-cross -O3 main.py     && \
   mpy-cross -O3 ds3231.py   && \
   mpy-cross -O3 max7219.py  && \
   mpy-cross -O3 font_4x6.py && \
   mpy-cross -O3 font_6x8.py
then
  echo "Start download"

  sudo ampy --port /dev/ttyUSB0 put main.py
  #sudo ampy --port /dev/ttyUSB0 put ds3231.mpy
  #sudo ampy --port /dev/ttyUSB0 put max7219.mpy
  #sudo ampy --port /dev/ttyUSB0 put font_4x6.mpy
  #sudo ampy --port /dev/ttyUSB0 put font_6x8.mpy
fi

