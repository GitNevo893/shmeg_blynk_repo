import smbus
bus=smbus.SMBus(1)
adress=0x27
bus.write_byte(adress, 0x01)
