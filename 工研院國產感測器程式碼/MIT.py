#!/usr/bin/python

import sys
import time
import difflib
import pigpio
import httplib
import urllib
import os
import datetime
import csv

file_name = "MIT_data_out"
path = "/home/pi/MIT/" + file_name
    
def bytes2hex(s):
    return "".join("{:02x}".format(c) for c in s)

def data_read(data_in):
    collect = [] 
    standard = "4d42"
    while True:
        index = data_in.find(standard)
        if index != -1:
            str_slice = data_in[index:index + 64]
            print(str_slice)
            if len(str_slice) == 64:
                data_in = data_in.replace(str_slice, "")
                new_list = []
                for x in str_slice:
                    new_list.append(x)
                single = int(new_list[12] + new_list[13] + new_list[14] + new_list[15], 16)
                collect.append(single) 
            else:
                break
        else:
            break
    current = datetime.datetime.now()
    for x in collect:
        line = []
        line.append(x)
        line.append(current.hour)
        line.append(current.minute)
        line.append(current.second)
        line.append(current.day)
        line.append(current.month)
        print("pmdata + time", line)
        with open(path, "a") as csvFile:
            print("open success")
            out_write = csv.writer(csvFile)
            out_write.writerow(line)

def data_upload(pmdata, num):
    API_key = "7OPOX3AVUEW7SEBJ"
    print("API_key: ",API_key)    
    
    if num == 1:
        params = urllib.urlencode({'field1': pmdata, 'key':API_key})
    elif num == 2:
        params = urllib.urlencode({'field2': pmdata, 'key':API_key})
    elif num == 3:
        params = urllib.urlencode({'field3': pmdata, 'key':API_key})
    elif num == 4:
        params = urllib.urlencode({'field4': pmdata, 'key':API_key})
    elif num == 5:
        params = urllib.urlencode({'field5': pmdata, 'key':API_key})

    headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
    tconn = httplib.HTTPConnection("api.thingspeak.com:80")
    tconn.request("POST", "/update", params, headers)
    response = tconn.getresponse()
    data = response.read()
    tconn.close()
    time.sleep(0.5)
    
def fun(RX):
    try:
        pi = pigpio.pi()
        pi.set_mode(RX, pigpio.INPUT)
        pi.bb_serial_read_open(RX, 9600, 8)
        time.sleep(0.5)
        for x in range(5):
            print("x:",x)
            (count, data) = pi.bb_serial_read(RX)
            if count != 0:
                data_hex = bytes2hex(data)
                print("data_hex",data_hex)
                data_read(data_hex)
                # data_upload(pmdata, num)
            time.sleep(1) 

        print("close")
        pi.bb_serial_read_close(RX)
        pi.stop()

    except Exception as e:
        print(e)
        print("close")
        # pi.bb_serial_read_close(RX)
        pi.stop()

def main():
    RX = [18]
    num = 1
    try:
        os.system("sudo pigpiod")
        os.system("export PIGPIO_ADDR=soft, export PIGPIO_PORT=8888")
        while 1:
            for rx in RX:
                print("{} RX".format(rx))
                fun(rx)
            print("it's time to sleep") 
            time.sleep(300)

    except KeyboardInterrupt:
        print("close")
        
if __name__ == "__main__":
    main()


