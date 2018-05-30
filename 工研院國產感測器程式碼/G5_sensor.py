#!/usr/bin/python
import sys
import time
import difflib
import pigpio
import httplib
import urllib
import datetime
import csv
import os

RX = 18
# API_key = "YAFYMHZWAA33M2PG"
file_name = "G5_data_out"
path = "/home/pi/MIT/" + file_name
standard = "424d001c"

def Check_status():
    if os.path.exists(path):
        os.remove(path)
        print("exist")

def data_read(data_in):
    while True:
        current = datetime.datetime.now()
        index = data_in.find(standard)
        # print("index", index)
        if index != -1:
            str_slice = data_in[index:index + 64]
            print(str_slice)
            if len(str_slice) == 64:
                data_in = data_in.replace(str_slice, "")
                new_list = []
                for x in str_slice:
                    new_list.append(x)
                    
                # pm1 = int(new_list[20] + new_list[21] + new_list[22] + new_list[23], 16)
                pm25 = int(new_list[24] + new_list[25] + new_list[26] + new_list[27], 16)
                # pm10 = int(new_list[28] + new_list[29] + new_list[30] + new_list[31], 16)
                collect = []
                collect.append(pm25)
                collect.append(current.hour)
                collect.append(current.minute)
                collect.append(current.second)
                collect.append(current.day)
                collect.append(current.month)
                print("collect", collect)
                csvFile = open(path, "a")
                print("open success")
                out_write = csv.writer(csvFile)
                out_write.writerow(collect)
                csvFile.close()
            else:
                break
        else:
            break
            
def bytes2hex(s):
    return "".join("{:02x}".format(c) for c in s)

def data_upload(pmdata):
    params = urllib.urlencode({'field1': pmdata[0], 'field2': pmdata[1], 'field3': pmdata[2], 'key':API_key})
    headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
    tconn = httplib.HTTPConnection("api.thingspeak.com:80")
    tconn.request("POST", "/update", params, headers)
    response = tconn.getresponse()
    data = response.read()
    tconn.close()
    time.sleep(0.1)
    
def main():
    os.system("sudo pigpiod")
    os.system("export PIGPIO_ADDR=soft, export PIGPIO_PORT=8888")
    pi = pigpio.pi()
    pi.set_mode(RX, pigpio.INPUT)
    pi.bb_serial_read_open(RX, 9600, 8)
    time.sleep(0.1)
    try:
        # Check_status()
        while 1:
            print("DATA")
            (count, data) = pi.bb_serial_read(RX)
            if count:
                data_hex = bytes2hex(data)
                print("data hex",data_hex)
                data_read(data_hex)
                # data_upload(pmdata)
            time.sleep(1)
    except (KeyboardInterrupt, Exception) as w:
        print("close")
        print(w)
        pi.bb_serial_read_close(RX)
        pi.stop()

if __name__ == "__main__":
    main()

