#!/usr/bin/env/python

import serial
import requests
import time
import datetime
from bme280 import readBME280All


todayStr = ""
tomorrowStr=""
xrate = 1
e = b"\xff\xff\xff"
myCalUrl = "https://script.google.com/macros/s/AKfycbwY2YIhEJeJc3GbmubJ4diF-R8mYYCfEiHH49LnxS70AvGRPskt/exec"
myCurUrl = "http://data.fixer.io/api/latest?access_key=0a371f7901a6260a0ea11865f1ad98da&symbols=TWD,GBP&format=1"

def getCal(url):
    global todayStr
    global tomorrowStr
    try:
        resp = requests.get(url)
    except:
        return ("REQUEST ERROR")
        exit
    #print("Response: "  + str(resp.status_code))
    if resp.status_code==200:
        #print(resp.content)
        root = resp.json()
        todayStr = "\\r Today"
        for i in range(10):
            try:
                ttitle = root["eventsToday"][i]["title"]
            except:
                break
            ttime = root["eventsToday"][i]["time"]
            tevent = str("\\r  ") + ttitle + str(" ") + ttime
            todayStr += tevent;
    
        #print(todayStr)

        tomorrowStr = "\\r\\r Tomorrow"
        for j in range(10):
            try:
                mtitle = root["eventsTomro"][j]["title"]
            except:
                break
            mtime = root["eventsTomro"][j]["time"]
            mevent = str("\\r  ") + mtitle + str(" ") + mtime
            tomorrowStr += mevent
    
        #print(tomorrowStr)
        return("OK")
    else:
        return("INCORRECT STATUS CODE")
        
def getCurr(url):
    global xrate
    try:
        resp = requests.get(url)
    except:
        return ("REQUEST ERROR")
        exit
    #print("Response: "  + str(resp.status_code))
    if resp.status_code==200:
        #print(resp.content)
        root = resp.json()  
        GBPrate = root["rates"]["GBP"]
        TWDrate = root["rates"]["TWD"]
        xrate = TWDrate / GBPrate
        return("OK")
    else:
        return("INCORRECT STATUS CODE")
                
ser = serial.Serial(
    port = '/dev/ttyAMA0',
    baudrate = 9600,
    stopbits = serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=5)

if serial.VERSION <= "3.0":
    if not ser.isOpen():
        ser.open()
else:
    if not ser.is_open:
        ser.open()

#initial call to get values for display       
perror=getCal(myCalUrl)
if (perror != "OK" ) :
    print ("getCal() failed: "+perror)
    exit
else:               
    ser.write(b"cal.txt=\"" + todayStr.encode() + tomorrowStr.encode() + b"\""+e)

#initial call to get values for display               
perror=getCurr(myCurUrl)
if (perror != "OK" ) :
    print ("getCurr() failed: "+perror)
    exit
else:          
    ser.write(b"curr.txt=\"1GBP = " + b'%.2f'%xrate + b"NT$\"" + e )
        

t = time.time()
this_minute1 = t
this_minute2 = t
this_minute3 = t
######################## START LOOP ########################
while True:
    if time.time() != t:
        rn = datetime.datetime.now()
        ltime = rn.strftime("%H:%M:%S")
        daydate = rn.strftime("%A, %d %B %Y")  
        ser.write(b'time.txt=\"' + ltime.encode() + b'\"'+ e)
        ser.write(b'daydate.txt=\"' + daydate.encode() + b'\"'+ e)
        
        t = time.time()
# Crude scheduler to get BME280 readings every 10 secs
    if time.time() >= this_minute1 + 10:
        #print("getBME")
        ltemp, lpres, lhum = readBME280All()
        ser.write(b'temp.txt=\"' + b'%.2f'%ltemp + b'C\"' + e)
        ser.write(b'hum.txt=\"' + b'%.2f'%lhum + b'%RH\"' + e)
        ser.write(b'pres.txt=\"' + b'%.1f'%lpres + b'hPa\"' + e)
        #print(ltime)
        this_minute1 = time.time()
# Crude scheduler to get Google calendar every 30 mins
    if time.time() >= this_minute2 + 1800:
        perror=getCal(myCalUrl)
        #print("getCal")
    if (perror != "OK" ) :
        print ("getCal() failed: "+perror)
        exit
    else:               
        ser.write(b"cal.txt=\"" + todayStr.encode() + tomorrowStr.encode() + b"\""+e)
        this_minute2 = time.time()
# Crude scheduler to get currency conversion every hour
    if time.time() >= this_minute3 + 3600:
        perror=getCurr(myCurUrl)
    if (perror != "OK" ) :
        print ("getCurr() failed: "+perror)
        exit
    else:               
        ser.write(b"curr.txt=\"1GBP = " + b'%.2f'%xrate + b"NT$\"" + e )
        this_minute3 = time.time()
        
  
