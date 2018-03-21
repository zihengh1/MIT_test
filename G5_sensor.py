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

RX = 15
API_key = "YAFYMHZWAA33M2PG"

def data_read(data_in):
    collect = [0, 0, 0]
    times = 0
    standard = "424d001c"
    while True:
        index = data_in.find(standard)
        # print("index", index)
        if index != -1:
            str_slice = data_in[index:index + 64]
            times = times + 1
            print(str_slice)
            if len(str_slice) == 64:
                data_in = data_in.replace(str_slice, "")
                new_list = []
                for x in str_slice:
                    new_list.append(x)
                    #for x in range(0, len(str_slice), 4):
                        # print(new_list[x:x+4])
                        # ans = int(new_list[x] + new_list[x + 1] + new_list[x + 2] + new_list[x + 3], 16)
                    # print(ans)
                pm1 = int(new_list[20] + new_list[21] + new_list[22] + new_list[23], 16)
                pm25 = int(new_list[24] + new_list[25] + new_list[26] + new_list[27], 16)
                pm10 = int(new_list[28] + new_list[29] + new_list[30] + new_list[31], 16)
                collect[0] = (pm1 + collect[0])
                collect[1] = (pm25 + collect[1])
                collect[2] = (pm10 + collect[2])
                # print("collect", collect)
            else:
                break
        else:
            break
    if times != 0:
        collect = [round(x / times, 2) for x in collect]
    time.sleep(1)
    return collect

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
    
def Check_status(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print("exist")
    return True

def output_a_file(pmdata):
    current = datetime.datetime.now()
    pmdata.append(current.hour)
    pmdata.append(current.minute)
    pmdata.append(current.second)
    print("pmdata + time", pmdata)
    file_name = "G5_data_out"
    path = "/home/pi/FINAL_code/" + file_name
    print("path", path)
    with open(path, "a") as csvFile:
        print("open success")
        out_write = csv.writer(csvFile)
        out_write.writerow(pmdata)

def main():
    pi = pigpio.pi()
    pi.set_mode(RX, pigpio.INPUT)
    # pi.bb_serial_read_close(RX)
    pi.bb_serial_read_open(RX, 9600, 8)
    time.sleep(0.1)
    try:
        while 1:
            (count, data) = pi.bb_serial_read(RX)
            if count:
                data_hex = bytes2hex(data)
                print("data hex",data_hex)
                pmdata = data_read(data_hex)
                # print("pmdata", pmdata)
                data_upload(pmdata)
                output_a_file(pmdata)
            time.sleep(60)
    except (KeyboardInterrupt, Exception):
        print("close")
        pi.bb_serial_read_close(RX)
        pi.stop()

if __name__ == "__main__":
       main()
