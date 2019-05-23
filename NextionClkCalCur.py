#!/usr/bin/python3

import serial
import requests
import time
import datetime
import serinit
from bme280 import readBME280All
from getcal import getCal
from getcurr import getCurr


myCalUrl = "https://script.google.com/macros/s/AKfycbwY2YIhEJeJc3GbmubJ4diF-R8mYYCfEiHH49LnxS70AvGRPskt/exec"
myCurUrl = "http://data.fixer.io/api/latest?access_key=0a371f7901a6260a0ea11865f1ad98da&symbols=TWD,GBP&format=1"

e = serinit.e
ser=serinit.serInit()

#initial calls to get values for display   

try:
    tdyStr, tmwStr = getCal(myCalUrl) 
    ser.write(b"cal.txt=\"" + tdyStr.encode() + tmwStr.encode() + b"\""+e)
except:
    ser.write(b"cal.txt=\"No calendar data\""+e)
try:
    xrate = getCurr(myCurUrl)
    ser.write(b"curr.txt=\"1GBP = " + b'%.2f'%xrate + b"NT$\"" + e )
except:
    ser.write(b"curr.txt=\"No exchange data\"" + e )    
    
######################## START LOOP ########################

t = time.time()
time_now1 = t
time_now2 = t
time_now3 = t

while True:
    if time.time() != t:
        rn = datetime.datetime.now()
        ltime = rn.strftime("%H:%M:%S")
        daydate = rn.strftime("%A, %d %B %Y")  
        ser.write(b'time.txt=\"' + ltime.encode() + b'\"'+ e)
        ser.write(b'daydate.txt=\"' + daydate.encode() + b'\"'+ e)
        
        t = time.time()

# Crude scheduler to get BME280 readings every 10 secs
    if time.time() >= time_now1 + 10:
        try:
            ltemp, lpres, lhum = readBME280All()
            ser.write(b'temp.txt=\"' + b'%.2f'%ltemp + b'C\"' + e)
            ser.write(b'hum.txt=\"' + b'%.2f'%lhum + b'%RH\"' + e)
            ser.write(b'pres.txt=\"' + b'%.1f'%lpres + b'hPa\"' + e)
        except:
            ser.write(b'temp.txt=\"No data\"' + e)
            ser.write(b'hum.txt=\"No data\"' + e)
            ser.write(b'pres.txt=\"No data\"' + e)
        time_now1 = time.time()

# Crude scheduler to get Google calendar every 30 mins
    if time.time() >= time_now2 + 1800:
        try:
            tdyStr, tmwStr = getCal(myCalUrl) 
            ser.write(b"cal.txt=\"" + tdyStr.encode() + tmwStr.encode() + b"\""+e)
        except:
            ser.write(b"cal.txt=\"No calendar data\""+e)
        time_now2 = time.time()

# Crude scheduler to get currency conversion every hour
    if time.time() >= time_now3 + 3600:
        try:
            xrate = getCurr(myCurUrl)
            ser.write(b"curr.txt=\"1GBP = " + b'%.2f'%xrate + b"NT$\"" + e )
        except:
            ser.write(b"curr.txt=\"No exchange data\"" + e )    
        time_now3 = time.time()
        
  
