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
WIFI_SSID="Awesome"
WIFI_PASSWORD="pr14052008"
WIFI_SSID="WIFI_Hugim"
WIFI_PASSWORD="H@123456"
BLYNK_AUTH="fU23BptiMdprQD_ja9ks-fpYzFL2g16c"
WRITE_URL=f"https://blynk.cloud/external/api/update?token={BLYNK_AUTH}"
READ_URL=f"https://blynk.cloud/external/api/get?token={BLYNK_AUTH}"
# Blynk virtual pins configuration
cells=[0, "V0", "V2", "V4", "V6", "V8", "V10", "V12", "V14"]
cell_content=[0, "V1", "V3", "V5", "V7", "V9", "V11", "V13", "V15"]
cell_date=[0, "V19", "V20", "V21", "V22", "V23", "V24", "V25", "V26"]
missing="V16"
missing_cells="V17"
updates="V18"
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
            #lcd.putstr(".")
    print("Connected:", wlan.ifconfig())
# Send value to widget in Blynk
def blynk_write(pin, value):
    url = f"{WRITE_URL}&{pin}={value}"
    print("URL:", url)
    try:
        r = urequests.get(url)
        r.close()
        print(f"Sent {value} → {pin}")
    except Exception as e:
        print("Blynk write error:", e)
# Get the current value of widget from Blynk
def blynk_read(pin):
    url=f"{READ_URL}&{pin}"
    #print("Reading:", url)
    try:
        r=urequests.get(url)
        print("RAW:", r.text)
        val = r.text
        r.close()
        return val
    except Exception as e:
        print("Blynk read error:", e)
        return None
    
def make_str(time):
    string=""
    for i in time:
        string=string+str(i)+","
    return string
        
def read_updates():
    new_content=""
    new_date=()
    delete=False
    cell_num=0
    update=blynk_read(updates)
    if update[0]=="0":
        return
    update=update.strip(" ")
    update=update.split(",")
    for i in range(len(update)):
        update.append(update[0].strip(" "))
        update.pop(0)
    print(update)
    cell_num=int(update[0])
    if update[1]=="update":
        delete=False
    elif update[1]=="change":
        delete=True
    else:
        print("invalid request")
        return
    if update[2]=="content":
        new_content=update[3]
        if delete:
            blynk_write(cell_content[cell_num], new_content)
        else:
            old_content=blynk_read(cell_content[cell_num])
            blynk_write(cell_content[cell_num], old_content+","+new_content)
    elif update[2]=="date":
        for i in range(3,8):
            new_date=new_date+(int(update[i]),)
        new_date=new_date+(0,)
        new_date=new_date+(0,)
        new_date=new_date+(-1,)
        if delete:
            date_str=make_str(new_date)
            blynk_write(cell_date[cell_num], date_str)
        else:
            old_date=blynk_read(cell_date[cell_num])
            t_new=time.mktime(new_date)
            t_old=time.mktime(old_date)
            t=min(t_new, t_old)
            t=time.gmtime(t)
            date_str=make_str(t)
            blynk_write(cell_date[cell_num], date_str)
    else:
        print("invalid request")
        return
    print("update succeful!")
    return update

def check_expire(cell_num):
    time_expire=()
    epoch_time=time.time()
    date_expire=blynk_read(cell_date[cell_num])
    if time_expire=="0":
        print("no expired date")
        return
    date_expire=date_expire.strip(",")
    date_expire=date_expire.split(",")
    for i in range(0,6):
        time_expire=time_expire+(int(date_expire[i]),)
    time_expire=time_expire+(0,)
    time_expire=time_expire+(0,)
    time_expire=time_expire+(-1,)
    time_expire=time.mktime(time_expire)
    if time_expire>epoch_time:
        print("still good!")
    else:
        print("oh oh")
        blynk_write(missing, 1)
        blynk_write(missing_cells, blynk_read(missing_cells)+","+str(cell_num))
def check_all():
    for cell in range(1, len(cells)):
        check_expire(cell)

# Main loop
def main():
    connect_wifi()
    while True:
main()
