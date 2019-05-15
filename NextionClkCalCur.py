import serial
import requests
import time
import datetime
import bme280


todayStr = ""
tomorrowStr=""
xrate = 1
e = "\xff\xff\xff"
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
        ser.write("cal.txt=\"" + str(todayStr) + str(tomorrowStr)+ "\""+e)

#initial call to get values for display               
perror=getCurr(myCurUrl)
if (perror != "OK" ) :
        print ("getCurr() failed: "+perror)
        exit
else:          
		ser.write("curr.txt=\"1GBP = " + ('%.2f'%xrate) + "NT$\"" + e )
		

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
        ser.write('time.txt=\"' + ltime + '\"'+ e)
        ser.write('daydate.txt=\"' + daydate + '\"'+ e)
        
        t = time.time()
# Crude scheduler to get BME280 readings every 10 secs
    if time.time() >= this_minute1 + 10:
        ltemp, lpres, lhum = bme280.readBME280All()
        ser.write('temp.txt=\"' + ('%.2f'%ltemp) + 'C\"' + e)
        ser.write('hum.txt=\"' + ('%.2f'%lhum) + '%RH\"' + e)
        ser.write('pres.txt=\"' + ('%.1f'%lpres) + 'hPa\"' + e)
        #print(ltime)
        this_minute1 = time.time()
# Crude scheduler to get Google calendar every 30 mins
    if time.time() >= this_minute2 + (30 * 60):
        perror=getCal(myCalUrl)
	if (perror != "OK" ) :
                print ("getCal() failed: "+perror)
		exit
        else:               
		ser.write("cal.txt=\"" + str(todayStr) + str(tomorrowStr)+ "\""+e)
		this_minute2 = time.time()
# Crude scheduler to get currency conversion every hour
    if time.time() >= this_minute3 + (60 * 60):
        perror=getCurr(myCurUrl)
	if (perror != "OK" ) :
		print ("getCurr() failed: "+perror)
		exit
	else:               
		ser.write("curr.txt=\"1GBP = " + ('%.2f'%xrate) + "NT$\"" + e )
		this_minute3 = time.time()
        
  
