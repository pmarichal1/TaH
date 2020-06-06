#!/usr/bin/env python3
#############################################################################
# Filename    : DHT11.py
# Description :	read the temperature and humidity data of DHT11
# Author      : freenove
# modification: 2018/08/03
########################################################################
import RPi.GPIO as GPIO
import time
import os
import Freenove_DHT as DHT
import LCD
#import Blink
import pickle
import socket
from datetime import datetime

# time function
DHTPin = 15     #define the pin of DHT11
buttonPin = 12    # define the buttonPin
ledPin = 11 #LED

def get_time_now():     # get system time
    return datetime.now().strftime(' %H:%M:%S')

def get_date_now():     # get system time
    return datetime.now().strftime('%A %B %D   %H:%M:%S')

testIP = "8.8.8.8"
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect((testIP, 0))
ipaddr = s.getsockname()[0]
host = socket.gethostname()
#print ("IP:", ipaddr, " Host:", host)

# main loop
def loop():
    GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
    dht = DHT.DHT(DHTPin)   #create a DHT class object
    GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set buttonPin's mode is input, and pull up to high level(3.3V)
    GPIO.setup(ledPin, GPIO.OUT)   # Set ledPin's mode is output
    GPIO.output(ledPin, GPIO.LOW) # Set ledPin low to off led
    sumCnt = 0              #number of reading times
    hi_temp = 0
    low_temp = 150
    hi_hum = 0
    low_hum = 110
    bad_reading=0
    temperature_list = []
    humidity_list = []
    list_size = 2000
    distance=0
    blinkLed = 1
    while(True):
        if GPIO.input(buttonPin)==GPIO.LOW:
            loopCnt=0
            buttonPressed=0
            LCD.run_lcd("Confirm Shutdown ","","","")
            time.sleep(3)
            while(loopCnt < 5):
                loopCnt= loopCnt+1
                print("DEBUG", loopCnt, buttonPressed)
                
                if GPIO.input(buttonPin)==GPIO.LOW:
                    buttonPressed = buttonPressed + 1
                if buttonPressed > 3:
                    LCD.run_lcd("Shutting Down Now ","","","")
                    print("Down", loopCnt, GPIO.input(buttonPin))
                    #shutdown when switch is held down
                    ##GPIO.cleanup()
                    ##os.system("shutdown now -h")
                if blinkLed == 1:
                    blinkLed  = 0
                else:
                    blinkLed = 1
                time.sleep(1)
            print("blinkLed", blinkLed, buttonPressed)

        time.sleep(3)
        #print(get_date_now())
        sumCnt += 1         #counting number of reading times
        chk = dht.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
        #print(" Length of list %d"%(len(temperature_list)))
        #print(len(temperature_list))
        #print ("The Loop Count  is : %d, \t chk    : %d"%(sumCnt,chk))
        #if (chk is dht.DHTLIB_OK):      #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
        #    print("DHT11,OK!")
        #elif(chk is dht.DHTLIB_ERROR_CHECKSUM): #data check has errors
        #    print("DHTLIB_ERROR_CHECKSUM!!")
        #elif(chk is dht.DHTLIB_ERROR_TIMEOUT):  #reading DHT times out
        #    print("DHTLIB_ERROR_TIMEOUT!")
        #else:               #other errors
        #    print("Other error!")
        dht.temperature = dht.temperature *(9/5) +32    
        #print temp and humidity to LCD
        temperature = float("%.2f" % dht.temperature)
        #if temperature > 0 and dht.humidity > 0:
        print("LOOPING")
        if chk == 0:
            print("Good Reading", blinkLed)
            if blinkLed == 1:
                GPIO.output(ledPin, GPIO.HIGH)  # led on
            LCD.run_lcd("Temp F ", str(temperature),"Humidity % ", dht.humidity)
            if len(temperature_list) > list_size:
                temperature_list.pop(0)
                humidity_list.pop(0)
            temperature_list.extend([temperature])
            humidity_list.extend([dht.humidity])
            temp_average = sum(temperature_list) / len(temperature_list)
            hum_average = sum(humidity_list) / len(humidity_list) 

            #temp file to lock file reader for plotting
            f = open("/home/pi/Projects/Device/TaH/lock.txt", 'w')
            with open('/home/pi/Projects/Device/TaH/envfile.data', 'wb') as filehandle:  
                # store the data as binary data stream
                pickle.dump(temperature_list, filehandle)
                pickle.dump(humidity_list, filehandle)
                pickle.dump(distance, filehandle)
            f.close()
            os.remove("/home/pi/Projects/Device/TaH/lock.txt")
            # need to compensate for bad numbers so can't increase or decrease more than 15% in one sample
            if temperature > hi_temp and temperature < (temp_average*1.15):
                hi_temp = temperature
            if temperature < low_temp and temperature > (temp_average - (temp_average*.15)):
                low_temp = temperature
            if dht.humidity > hi_hum and dht.humidity < (hum_average*1.15):
                hi_hum = dht.humidity
            if dht.humidity < low_hum and dht.humidity > (hum_average - (hum_average*.15)):
                low_hum = dht.humidity
            GPIO.output(ledPin, GPIO.LOW) # led off
            #print("Current Humidity :     %.2f, \t Current Temperature :     %.2f"%(dht.humidity, temperature))
            #print("Average Humidity :     %.2f, \t Average Temperature :     %.2f"%(hum_average, temp_average))
            #print("Hi Humidity :          %.2f, \t Hi Temperature :          %.2f"%(hi_hum, hi_temp))
            #print("Low Humidity :         %.2f, \t Low Temperature :         %.2f"%(low_hum, low_temp))
        else:
            bad_reading+=1
            #LCD.run_lcd("Bad DHT Reading ","","","")
            print("Bad DHT Read")



        #print(temperature_list)
        #print(humidity_list) 
        #print("Bad reads = %d %%\n"%((bad_reading/sumCnt)*100))
        time.sleep(3)
        LCD.run_lcd("Time",get_time_now(),"",ipaddr)
        time.sleep(3)

        
if __name__ == '__main__':
    #print ('Program is starting ... ')
    try:
        loop()
    except KeyboardInterrupt:
        GPIO.cleanup()
        GPIO.output(ledPin, GPIO.LOW) # Set ledPin low to off led
        exit()  

