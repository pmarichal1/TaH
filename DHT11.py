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
import numpy as np

DHTLIB_OK              = 0;
#DHTLIB_CHECKSUM  = -1;
#DHTLIB_TIMEOUT   = -2;
#DHTLIB_INVALID   = -999;

#import Blink
import pickle
import socket
from datetime import datetime

# time function
DHTPin = 15     #define the pin of DHT11
buttonPin = 12    # define the buttonPin
ledPin = 11 #LED
valueDifferentialMinus = .50
valueDifferentialPlus = 1.50
import sys
import numpy as np
 
# approximation valid for
# 0 degC < T < 60 degC
# 1% < RH < 100%
# 0 degC < Td < 50 degC 
 
# constants
a = 17.271
b = 237.7 # degC

 
def dewpoint_approximation(T,RH):
 
    Td = (b * gamma(T,RH)) / (a - gamma(T,RH))
 
    return Td
 
 
def gamma(T,RH):
 
    g = (a * T / (b + T)) + np.log(RH/100.0)
 
    return g

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
    prev_temp = 50
    prev_hum = 50
    prev_dewp = 50
    dewPoint = 50
    bad_reading=0
    good_reading=0
    temperature_list = []
    humidity_list = []
    dewp_list = []
    list_size = 9000
    distance=0
    blinkLed = 1
    firstPass = 0
    while(True):
        if GPIO.input(buttonPin)==GPIO.LOW:
            # shutdown box or stop flashing the LED during samples.
            # if the button is clicked, the LED stops flashing
            # if the button is pressed for 10 seconds, the box powers down
            loopCnt=0
            buttonPressed=0
            LCD.run_lcd("Confirm Shutdown ","","","")
            time.sleep(3)
            while(loopCnt < 5):
                loopCnt= loopCnt+1
                
                if GPIO.input(buttonPin)==GPIO.LOW:
                    buttonPressed = buttonPressed + 1
                    if blinkLed == 1:
                        blinkLed  = 0
                    else:
                        blinkLed = 1
                if buttonPressed > 3:
                    LCD.run_lcd("Shutting Down ","","","")
                    #shutdown when switch is held down
                    GPIO.cleanup()
                    os.system("shutdown now -h")

                time.sleep(1)

        #print(get_date_now())
        sumCnt += 1         #counting number of reading times
        chk = dht.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
        dht.temperature = dht.temperature *(9/5) +32    
        #print temp and humidity to LCD
        temperature = float("%.2f" % dht.temperature)
        if chk == DHTLIB_OK and dht.humidity < 100:
            dewPoint = dewpoint_approximation(dht.temperature,dht.humidity)
            dewPoint = float("%.2f" % dewPoint)
            prev_dewp = dewPoint
            good_reading +=1
            if blinkLed == 1:
                GPIO.output(ledPin, GPIO.HIGH)  # led on
                print("LED ON")
            LCD.run_lcd("Temp F ", str(temperature),"Humidity % ", dht.humidity)
            time.sleep(5)
            if dewPoint < 50:
                dewPtext = "ok"
            elif dewPoint > 65:
                dewPtext = "Very High"
            else:
                dewPtext = "High"
            
            LCD.run_lcd("DewP F ", str(dewPoint), "", dewPtext)

            if firstPass == 0:
                temp_average = temperature
                hum_average = dht.humidity
                firstPass = 1
            else:
                temp_average = sum(temperature_list) / len(temperature_list)
                hum_average = sum(humidity_list) / len(humidity_list)
            # following logic manages bad value from DHT
            if temperature > (temp_average - (temp_average*valueDifferentialMinus)) and temperature < (temp_average*valueDifferentialPlus):
                prev_temp = temperature
            else:
                temperature = prev_temp
                print("Bad Temp Value", temperature, " ", sumCnt)

            if dht.humidity > (hum_average - (hum_average*valueDifferentialMinus)) and dht.humidity < (hum_average*valueDifferentialPlus):
                prev_hum = dht.humidity
            else:
                dht.humidity = prev_hum
                print("Bad Hum Value",dht.humidity, " ", sumCnt)

            if len(temperature_list) > list_size:
                temperature_list.pop(0)
                humidity_list.pop(0)
                dewp_list.pop(0)
                
            temperature_list.extend([temperature])
            humidity_list.extend([dht.humidity])
            dewp_list.extend([dewPoint])

            #temp file to lock file reader for plotting
            #f = open("/home/pi/Projects/Device/TaH/lock.txt", 'w')
            f = open("./lock.txt", 'w')
            #with open('/home/pi/Projects/Device/TaH/envfile.data', 'wb') as filehandle:  
            with open('./envfile.data', 'wb') as filehandle: 
                # store the data as binary data stream
                pickle.dump(temperature_list, filehandle)
                pickle.dump(humidity_list, filehandle)
                pickle.dump(dewp_list, filehandle)
                pickle.dump(distance, filehandle)
            f.close()
            #os.remove("/home/pi/Projects/Device/TaH/lock.txt")
            os.remove("./lock.txt")
            #GPIO.output(ledPin, GPIO.LOW) # led off
# failed reading DHT
        else:
            temperature = prev_temp
            dht.humidity = prev_hum
            dewPoint = prev_dewp
            if len(temperature_list) > list_size:
                temperature_list.pop(0)
                humidity_list.pop(0)
                dewp_list.pop(0)
            temperature_list.extend([temperature])
            humidity_list.extend([dht.humidity])
            dewp_list.extend([dewPoint])

            #temp file to lock file reader for plotting
            f = open("./lock.txt", 'w')
            with open('./envfile.data', 'wb') as filehandle:  
                # store the data as binary data stream
                pickle.dump(temperature_list, filehandle)
                pickle.dump(humidity_list, filehandle)
                pickle.dump(dewp_list,filehandle)
                pickle.dump(distance, filehandle)
            f.close()
            os.remove("./lock.txt")
            #GPIO.output(ledPin, GPIO.LOW) # led off
            bad_reading+=1
            if chk == -1:
                LCD.run_lcd("Bad DHT Read ",str(chk),"DHTLIB_CHECKSUM","")
            elif chk == -2:
                LCD.run_lcd("Bad DHT Read ",str(chk),"DHTLIB_TIMEOUT","")
            else:
                LCD.run_lcd("Bad DHT Read ",str(chk),"DHTLIB_INVALID","")
            
            time.sleep(5)
            LCD.run_lcd("Temp F ", str(temperature),"Humidity % ", dht.humidity)
            time.sleep(5)
            if dewPoint < 50:
                dewPtext = "ok"
            elif dewPoint > 65:
                dewPtext = "Very High"
            else:
                dewPtext = "High"
            
            LCD.run_lcd("DewP F ", str(dewPoint), "", dewPtext)


        time.sleep(5)
        GPIO.output(ledPin, GPIO.LOW) # led off
        print("LED OFF")
        LCD.run_lcd("Time",get_time_now(),"",ipaddr)
        time.sleep(2)
        LCD.run_lcd("Bad Readings ",str(bad_reading)," Good ",str(good_reading))
        time.sleep(2)


        
if __name__ == '__main__':
    #print ('Program is starting ... ')
    try:
        loop()
    except KeyboardInterrupt:
        GPIO.cleanup()
        GPIO.output(ledPin, GPIO.LOW) # Set ledPin low to off led
        exit()  

