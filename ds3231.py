# MicroPython DS3231 RTC driver, I2C interface for ESP8266/ESP32

from machine import Pin, I2C
import ucollections
import utime

"""
 ESP32     | DS3231 for Pi
 ----------+--------------
 3.3       | 1 - VCC (+)
 D21 (SDA) | 2 - SDA
 D22 (SCL) | 3 - SCL
           | 4 - NC
 GND       | 5 - GND
"""

DateTimeTuple = ucollections.namedtuple("DateTimeTuple",
  ["year", "month", "day", "weekday", "hour", "minute", "second", "millisecond"])

def datetime_tuple(year, month, day, weekday=0, hour=0, minute=0,
                   second=0, millisecond=0):
  return DateTimeTuple(year, month, day, weekday, hour, minute,
                       second, millisecond)

def bcd2bin(value):
  return value - 6 * (value >> 4)

def bin2bcd(value):
    return value + 6 * (value // 10)

def tuple2seconds(datetime):
  return utime.mktime((datetime.year, datetime.month, datetime.day,
    datetime.hour, datetime.minute, datetime.second, datetime.weekday, 0))

def seconds2tuple(seconds):
  year, month, day, hour, minute, second, weekday, _yday = utime.localtime()
  return DateTimeTuple(year, month, day, weekday, hour, minute, second, 0)

class ds3231:
  DATETIME_REGISTER    = 0x00
  TEMPERATURE_REGISTER = 0x11  

  def __init__(self, sclPin=Pin(22), sdaPin=Pin(21), address=104):
    self.address = address
    self.i2c = I2C(scl=sclPin, sda=sdaPin, freq=100000)
    scan = self.i2c.scan()
    if address not in scan:
      print("error: DS3231 not found on I2C bus")
    print("i2c.scan():", scan)
    self.get()
    self.temp()


  def get(self):
    buf = bytearray(7)
    buf = self.i2c.readfrom_mem(self.address, self.DATETIME_REGISTER, 7)
    #print(buf) # FIXME
    self.dt = datetime_tuple(
                year=bcd2bin(buf[6]) + 2000,
                month=bcd2bin(buf[5]),
                day=bcd2bin(buf[4]),
                weekday=bcd2bin(buf[3]),
                hour=bcd2bin(buf[2]),
                minute=bcd2bin(buf[1]),
                second=bcd2bin(buf[0]),
            )
    return self.dt


  def set(self, datetime=(2018, 12, 31, 0, 23, 59, 59, 999)):
    buf = bytearray(7)
    datetime = datetime_tuple(*datetime)
    buf[0] = bin2bcd(datetime.second)
    buf[1] = bin2bcd(datetime.minute)
    buf[2] = bin2bcd(datetime.hour)
    buf[3] = bin2bcd(datetime.weekday)
    buf[4] = bin2bcd(datetime.day)
    buf[5] = bin2bcd(datetime.month)
    buf[6] = bin2bcd(datetime.year - 2000)
    retv = self.i2c.writeto_mem(self.address, self.DATETIME_REGISTER, buf)
    #print(buf)  # FIXME
    #print(retv) # FIXME
    self.get()


  def temp(self):
    buf = self.i2c.readfrom_mem(self.address, self.TEMPERATURE_REGISTER, 2)
    #print(buf[0], buf[1] >> 6) # FIXME
    temp = buf[0] + (buf[1] >> 6) * 0.25
    if temp > 127.:
      temp -= 256. # FIXME
    self.t = temp
    return temp

  def all(self):
      return self.dt, self.t

