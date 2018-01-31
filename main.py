# Demo clock on ESP32
import network
import socket
from machine import Pin, SPI, Timer
import time
from dht import DHT22
import onewire
import ds18x20
from ds3231 import *
import max7219
from font_4x6 import font_4x6 as FONT
import framebuf
import gc
gc.collect()

# setup Wi-Fi network
sta_if = network.WLAN(network.STA_IF)
sta_ap = network.WLAN(network.AP_IF)

"""
if False:
    # create AP
    sta_if.active(False)
    sta_ap.active(True)
    sta_ap.config(essid="esp-net", authmode=network.AUTH_WPA_WPA2_PSK, password="radio86rk")
    # IP address, netmask, gateway, DNS
    sta_ap.ifconfig(['192.168.1.1', '255.255.255.0', '192.168.1.1', '8.8.8.8'])

else:
    # connnect to AP
    sta_ap.active(False)
    sta_if.active(True)
    sta_if.connect('veonet', 'radio86rk')
    sta_if.ifconfig(['192.168.0.12', '255.255.255.0', '192.168.0.254', '192.168.0.254'])
    #sta_if.ifconfig()
"""

# DHT22 wrapper
class _DHT22_:
    def __init__(self, gpio_n):
        self.sensor = DHT22(Pin(gpio_n, Pin.IN, Pin.PULL_UP))
        self.t = 0
        self.h = 0
        self.m = True

    def run(self):
        if self.m:
            self.m = False
            self.sensor.measure() # poll DHT22 sensor
        else:
            self.m = True
            self.t = self.sensor.temperature()
            self.h = self.sensor.humidity()
            #print("DHT22: t=%f, h=%f" % (self.t, self.h))

    def get(self):
        return self.t, self.h

# DS18B22 wrapper
class _DS18B20_:
    def __init__(self, gpio_n):
        self.ow = onewire.OneWire(Pin(gpio_n)) # create a OneWire bus on pin
        self.ow.scan()  # return a list of devices on the bus
        self.ow.reset() # reset the bus
        self.ds = ds18x20.DS18X20(self.ow)
        self.t = 0
        self.m = True

    def run(self):
        if self.m:
            self.m = False
            self.roms = self.ds.scan()
            self.ds.convert_temp()
        else:
            self.m = True
            for rom in self.roms:
                self.t = self.ds.read_temp(rom)
                #print("DS18B20: t=%f" % self.t)

    def get(self):
        return self.t

# setup (h)SPI for MAX7219 with dot LED matrix
#if False:
if True:
    # hardware SPI (boudrate up to 80 MHz, real about from 1 kHz to 13.25 MHz)
    spi = SPI(1, baudrate=10000000, polarity=0, phase=0, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
else:
    # software SPI bus on the given pins (baudrate from 1 kHz to 500 kHz)
    # polarity is the idle state of SCK
    # phase=0 means sample on the first edge of SCK, phase=1 means the second
    spi = SPI(-1, baudrate=500000, polarity=0, phase=0, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
    #spi.init(baudrate=100000) # set the baudrate

CS = 27 # CS on D27 (GPIO-27)
NUM = 4 # number of 8x8 dot matrix blocks

display = max7219.Matrix8x8(spi, Pin(CS, Pin.OUT), NUM)
display.brightness(1) # [0..15]
display.fill(0)
display.show()

# put text (4x6 font) on frame buffer
def put_text(fbuf, text, x=0, y=0):
    for uchr in text:
        sym = FONT[ord(uchr)]
        for i in range(4):
            for j in range(6):
                fbuf.pixel(x + i, y + j,
                           1 if (sym[i] & (0x20 >> j)) else 0)
        x += 4


# DHT22 on GPIO-15
dht = _DHT22_(15)

# DS18B20 on GPIO-4
ds = _DS18B20_(4)

# RTC based on DS3231
rtc = ds3231(sclPin=Pin(22), sdaPin=Pin(21))
#rtc.set(datetime=(2017, 12, 16, 0, 23, 40, 00))

# blink blue LED 3 times
led = Pin(2, Pin.OUT) # blue LED
for i in range(3):
    led.value(1)
    display.fill(1)
    display.show()
    time.sleep_ms(250)
    led.value(0)
    display.fill(0)
    display.show()
    time.sleep_ms(250)

put_text(display, "HELLO!!!")
display.show()
time.sleep_ms(1000)


# FSM
cnt = 0
fsm = 0
days = ("SU", "MO", "TU", "WE", "TH", "FR", "SA")

def tick(timer):
    global dht, ds, rtc, cnt, fsm, days
    dht.run()
    ds.run()
    rtc.get()
    rtc.temp()

    # FSM
    cnt -= 1
    if cnt > 0:
        return

    # get data from sensors
    t1, h = dht.get()
    t2 = ds.get()
    dt, t3 = rtc.all()

    if fsm == 1:
        fsm = 2 # show temperature
        cnt = 3
        txt = "T=%.1f°" % t2

    elif fsm == 2:
        fsm = 3 # showh humidity
        cnt = 2
        txt = "H=%.1f%%" % h
    
    else: # fsm == 3
        fsm = 1 # show time
        cnt = 5
        txt = "%2s %02i:%02i" % (days[dt[3]], dt[4], dt[5])
    
    display.fill(0)
    put_text(display, txt, x=0, y=0)
    display.show()
    gc.collect()


# init periodic timer
timer = Timer(-1)
timer.init(period=1000, mode=Timer.PERIODIC, callback=tick)

"""
for i in range(2):
    dht.run()
    ds.run()
    rtc.get()
    rtc.temp()
"""

"""
# TCP server socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
                        
print('listening on', addr)
"""

# HTML template
html = """<!DOCTYPE html>
<html>
  <head><title>ESP32 &#043; DHT22 &#043; DS18B20 &#043; DS3231</title> </head>
  <body>
    <h1>DHT22:</h1>
    <h2>Temperature = %s &deg;C</h2>
    <h2>Humidity = %s &#037;</h2>
    <hr/>
    <h1>DS18B20:</h1>
    <h2>Temperature = %s &deg;C</h2>
    <hr/>
    <h1>DS3231:</h1>
    <h2>DateTime = %s</h2>
    <h2>Temperature = %s &deg;C</h2>
  </body>
</html>
"""

gc.collect()

"""
# Web server
while True:
    cl, addr = s.accept()
    #print('client connected from', addr)

    cl_file = cl.makefile('rwb', 0)
    while True:
        line = cl_file.readline()
        if not line or line == b'\r\n':
            break
    
    led.value(1)
    t1, h = dht.get()
    t2 = ds.get()
    dt, t3 = rtc.all()

    # format date and time to YYYY.MM.DD HH:MM:SS
    sdt = "%4i.%02i.%02i %02i:%02i:%02i" % \
          (dt[0], dt[1], dt[2], dt[4], dt[5], dt[6])

    response = html % (str(t1), str(h), str(t2), sdt, str(t3))
    cl.send(response)
    cl.close()

    led.value(0)
    gc.collect()
"""


