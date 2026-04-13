import smbus
from time import sleep
addr = 0x27
bus = smbus.SMBus(1)
def cmd(x):
    bus.write_byte(addr, x | 0x08)
def send(x, mode=0):
    high = mode | (x & 0xF0) | 0x08
    low  = mode | ((x<<4) & 0xF0) | 0x08
    bus.write_byte(addr, high); bus.write_byte(addr, high | 0x04); bus.write_byte(addr, high)
    bus.write_byte(addr, low);  bus.write_byte(addr, low  | 0x04); bus.write_byte(addr, low)
# init
for c in [0x33,0x32,0x28,0x0C,0x01]:
    send(c); sleep(0.005)
# print text
for ch in "c=8":
    send(ord(ch), 1)
