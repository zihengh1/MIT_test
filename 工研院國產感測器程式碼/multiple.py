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

file_name = "Multiple_data"
path = "/home/pi/MIT/" + file_name
    
def bytes2hex(s):
    return "".join("{:02x}".format(c) for c in s)

def data_read(data_in, num, now_time):
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
    for x in collect:
        line = []
				line.append(num)
        line.append(x)
        line.append(now_time.month) 
        line.append(now_time.day)
        line.append(now_time.hour)
        line.append(now_time.minute)
        line.append(now_time.second)
        print("pmdata + time", line)
        with open(path, "a") as csvFile:
            print("open success")
            out_write = csv.writer(csvFile)
            out_write.writerow(line)
    
def init_function(RX, num, now_time):
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
                data_read(data_hex, num, now_time)
            time.sleep(1) 

        print("close")
        pi.bb_serial_read_close(RX)
        pi.stop()

    except Exception as e:
        print(e)
        pi.stop()

def main():
    RX = [18, 23, 25, 12]
    try:
        os.system("sudo pigpiod")
        os.system("export PIGPIO_ADDR=soft, export PIGPIO_PORT=8888")
        while 1:
            for (index, rx) in enumerate(RX):
								current = datetime.datetime.now() 	
                print("{} RX".format(rx))
                init_function(rx, index, current)
            time.sleep(10)

    except KeyboardInterrupt:
        print("close")
        
if __name__ == "__main__":
    main()


