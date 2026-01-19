import network
import time
import urequests
from machine import Pin, ADC, I2C
from i2c_lcd import I2cLcd

#lcd
class I2cLcd:
    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.backlight = 0x08  # Backlight on
        self.row_offsets = [0x00, 0x40]  # 2-row LCD
        self._init_lcd()

    def _write_byte(self, data):
        self.i2c.writeto(self.i2c_addr, bytes([data | self.backlight]))

    def _pulse_enable(self, data):
        self._write_byte(data | 0x04)  # Enable high
        time.sleep_ms(1)
        self._write_byte(data & ~0x04) # Enable low
        time.sleep_ms(1)

    def _write4bits(self, data):
        self._write_byte(data)
        self._pulse_enable(data)

    def _send(self, value, mode=0):
        high = value & 0xF0
        low = (value << 4) & 0xF0
        self._write4bits(high | mode)
        self._write4bits(low | mode)

    def _init_lcd(self):
        time.sleep_ms(50)
        self._write4bits(0x30)
        time.sleep_ms(5)
        self._write4bits(0x30)
        time.sleep_ms(1)
        self._write4bits(0x30)
        self._write4bits(0x20)  # 4-bit mode

        # Function set: 2 lines, 5x8 dots
        self._send(0x28)
        # Display on, cursor off
        self._send(0x0C)
        # Clear display
        self.clear()
        # Entry mode
        self._send(0x06)

    def clear(self):
        self._send(0x01)
        time.sleep_ms(2)

    def move_to(self, col, row):
        if row >= self.num_lines:
            row = self.num_lines - 1
        addr = col + self.row_offsets[row]
        self._send(0x80 | addr)

    def putstr(self, string):
        for char in string:
            self._send(ord(char), mode=0x01)


i2c=I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
print(i2c.scan())
I2C_ADDR = 0x27
ROWS=2
COLS=16
lcd=I2cLcd(i2c, I2C_ADDR, ROWS, COLS)
lcd.clear()

# User configuration
WIFI_SSID="WIFI_Hugim"
WIFI_PASSWORD="H@340208"
WIFI_SSID="Awesome"
WIFI_PASSWORD="pr14052008"
BLYNK_AUTH="fU23BptiMdprQD_ja9ks-fpYzFL2g16c"
WRITE_URL=f"https://blynk.cloud/external/api/update?token={BLYNK_AUTH}"
READ_URL=f"https://blynk.cloud/external/api/get?token={BLYNK_AUTH}"
# Blynk virtual pins configuration
cells=[0, "V0", "V2", "V4", "V6", "V8", "V10", "V12", "V14"]
cell_content=[0, "V1", "V3", "V5", "V7", "V9", "V11", "V13", "V15"]
missing="V16"
missing_cells="V17"
# Initialize Pins
LED_PIN="LED"  
led=Pin("LED", Pin.OUT)

# Connect to Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            led.value(1)
            time.sleep(0.25)
            led.value(0)
            time.sleep(0.25)
            lcd.putstr(".")
    print("Connected:", wlan.ifconfig())
# Send value to widget in Blynk
def blynk_write(pin, value):
    url=f"{WRITE_URL}&{pin}={value}"
    print("URL:", url)
    try:
        r=urequests.get(url)
        r.close()
        print(f"Sent {value} → {pin}")
    except Exception as e:
        print("Blynk write error:", e)
# Get the current value of widget from Blynk
def blynk_read(pin):
    url=f"{READ_URL}&{pin}"
    print("Reading:", url)
    try:
        r=urequests.get(url)
        print("RAW:", r.text)
        val = r.text
        r.close()
        return val
    except Exception as e:
        print("Blynk read error:", e)
        return None
def check_expire:

# Main loop
def main():
    connect_wifi()
    while True:
        blynk_read(cells[1])
main()

