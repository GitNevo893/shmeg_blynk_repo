import smbus
from time import sleep
addr = 0x27
bus = smbus.SMBus(1)
def send(x, mode=0):
    high = mode | (x & 0xF0) | 0x08
    low  = mode | ((x << 4) & 0xF0) | 0x08
    bus.write_byte(addr, high)
    bus.write_byte(addr, high | 0x04)
    bus.write_byte(addr, high)
    bus.write_byte(addr, low)
    bus.write_byte(addr, low | 0x04)
    bus.write_byte(addr, low)
def init_lcd():
    for c in [0x33, 0x32, 0x28, 0x0C, 0x01]:
        send(c)
        sleep(0.005)
def write_line(text, line=1):
    if line==1:
        send(0x80)
    else:
        send(0xC0)
    for ch in text:
        send(ord(ch), 1)
def scroll_line(text, line=1, delay=0.3):
    #text = text + " " * 16
    for i in range(len(text) - 15):
        if line==1:
            send(0x80)
        else:
            send(0xC0)
        window = text[i:i+16]
        for ch in window:
            send(ord(ch), 1)
        sleep(delay)
init_lcd()
def message(line1, line2):
    write_line(line1, 1)
    if len(line2)<=16:
        write_line(line2, 2)
    else:
        scroll_line(line2, 2, 0.3)
message("yo world","aaaaaaahhhh help me heeeeelp aaaaaaaaaa")
    
        

    
            
