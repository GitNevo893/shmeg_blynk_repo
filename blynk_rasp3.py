import time
import requests
from gpiozero import LED, Button, MCP3008
#from smbus2 import SMBus

# User configuration
WIFI_SSID="Awesome"
WIFI_PASSWORD="pr14052008"
WIFI_SSID="WIFI_Hugim"
WIFI_PASSWORD="H@123456"
BLYNK_AUTH="fU23BptiMdprQD_ja9ks-fpYzFL2g16c"
WRITE_URL=f"https://blynk.cloud/external/api/update?token={BLYNK_AUTH}"
READ_URL=f"https://blynk.cloud/external/api/get?token={BLYNK_AUTH}"
# Blynk virtual pins configuration
cell_led=[0, "V0", "V2", "V4", "V6", "V8", "V10", "V12", "V14", "V27"]
cell_content=[0, "V1", "V3", "V5", "V7", "V9", "V11", "V13", "V15", "V28"]
cell_date=[0, "V19", "V20", "V21", "V22", "V23", "V24", "V25", "V26", "V29"]
missing="V16"
missing_cells="V17"
updates="V18"
# Initialize Pins

# Send value to widget in Blynk
def blynk_write(pin, value):
    url = f"{WRITE_URL}&{pin}={value}"
    print("URL:", url)
    try:
        r = requests.get(url, timeout=5)
        print(f"Sent {value} → {pin}")
    except Exception as e:
        print("Blynk write error:", e)

# Get the current value of widget from Blynk
def blynk_read(pin):
    url = f"{READ_URL}&{pin}"
    try:
        r = requests.get(url, timeout=5)
        return r.text.strip()
    except Exception as e:
        print("Blynk read error:", e)
        return None
    
def make_str(l1st):
    string=""
    for i in range(len(l1st)):
        string=string+str(l1st[i])
        if i<(len(l1st)-1):
            string=string+","
    return string
        
def read_updates():
    new_content=""
    old_content=""
    new_date=()
    old_date=()
    delete=False
    cell_num=0
    update=blynk_read(updates)
    update=update.strip(" ")
    update=update.split(",")
    for i in range(len(update)):
        update.append(update[0].strip(" "))
        update.pop(0)
    print(update)
    if update[0]=="0" or update[0]=="on" or update[0]=="off":
        return
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
            try:
                old_content=blynk_read(cell_content[cell_num])
                old_content=old_content.strip(" ")
                old_content=old_content.split(",")
                for item in old_content:
                    if new_content==item:
                        print("already in content")
                        return
                blynk_write(cell_content[cell_num], make_str(old_content)+","+new_content)
            except:
                print("peleg dont forget to check this alright man")
                blynk_write(cell_content[cell_num], new_content)            
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
            try:
                old_update=blynk_read(cell_date[cell_num])
                old_update=old_update.strip(" ")
                old_update=old_update.split(",")
                for i in range(3,8):
                    old_date=new_date+(int(old_update[i]),)
                old_date=old_date+(0,)
                old_date=old_date+(0,)
                old_date=old_date+(-1,)
                t_new=time.mktime(new_date)
                t_old=time.mktime(old_date)
                t=min(t_new, t_old)
                t=time.gmtime(t)
                date_str=make_str(t)
                blynk_write(cell_date[cell_num], date_str)
            except:
                date_str=make_str(new_date)
                blynk_write(cell_date[cell_num], date_str)
                return
    else:
        print("invalid request")
        return
    print("update succeful! "+update[1]+"d cell "+update[0],"' "+update[2])
    return update

def check_expire(cell_num):
    global is_missing
    time_expire=()
    epoch_time=time.time()
    date_expire=blynk_read(cell_date[cell_num])
    if date_expire=="" or date_expire=="0":
        print("no expired date")
        return
    try:
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
            is_missing=True
            blynk_write(missing, 1)
            old=blynk_read(missing_cells)
            old=old.strip(" ")
            old=old.split(",")
            for cell in old:
                if str(cell_num)==cell:
                    print("already missing")
                    return
            blynk_write(missing_cells, blynk_read(missing_cells)+","+str(cell_num))
    except:
        print("nah")
        
def check_all():
    global is_missing
    for cell in range(1, len(cell_date)):
        check_expire(cell)
    if is_missing:
        blynk_write(missing, 1)
    else:
        blynk_write(missing, 0)
        
on=False
def is_on():
    global on
    command=blynk_read(updates)
    if command=="off":
        on=False
    elif command=="on":
        on=True
    else:
        return
#def light(cell_num, value):
    #cell_pin[cell_num].value()
#def leds():
    #value=0
    #for cell in range(cell_led):
        #value=blynk_read(cell_led[cell])
        #light(cell, value)

# Main loop
def main():
    while True:
        is_on()
        if True:
            read_updates()
            check_all()
        time.sleep(0.5)
main()
