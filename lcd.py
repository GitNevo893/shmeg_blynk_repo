import smbus
bus=smbus.SMBus(1)
adress=0x27
bus.write_byte(adress, 0x01)
from RPLCD.i2c import CharLCD
lcd = CharLCD('PCF8574', 0x27)
lcd.write_string("Hello!")
