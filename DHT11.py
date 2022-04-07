#!/usr/bin/env python3
#############################################################################
# Filename    : DHT11.py
# Description :	read the temperature and humidity data of DHT11
# Author      : freenove
# modification: 2018/08/03
########################################################################
import RPi.GPIO as GPIO
import time
from datetime import datetime
import os
import Freenove_DHT as DHT
import numpy as np
import math
#import Adafruit_DHT

DHTLIB_OK              = 0;
#DHTLIB_CHECKSUM  = -1;
#DHTLIB_TIMEOUT   = -2;
#DHTLIB_INVALID   = -999;

#import Blink
import pickle
import socket
from datetime import datetime
LCD_ENABLED = 0
if LCD_ENABLED:
    import LCD

# time function
DHTPin = 15     #define the pin of DHT11
#DHT2_SENSOR = Adafruit_DHT.DHT22
#DHT2_PIN = 4

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
SAMPLE_TIME = 30

# Dewpoint calculation
def calc_dewpoint(tempC, rlHum):

    r  = 8314.3
    mw = 18.016

    if tempC >= 0:
        a = 7.5
        b = 237.3
    # over water:
    # elif tempC < 0:
    #     a = 7.6
    #     b = 240.7
    #
    # over ice:
    elif tempC < 0:
        a = 9.5
        b = 265.5

    saettDampfDruck = 6.1078 * 10**((a*tempC)/(b+tempC))
    dampfDruck = rlHum / 100.0 * saettDampfDruck
    v = math.log10(dampfDruck/6.1078)
    dewpC = b*v/(a-v)
    dewpF = dewpC *(9/5) +32  
    return dewpF
 
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
print("STARTING DHT11")
testIP = "8.8.8.8"
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect((testIP, 0))
ipaddr = s.getsockname()[0]
host = socket.gethostname()
print ("IP:", ipaddr, " Host:", host)

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
    sampledate_list = []
    list_size = 900000
    firstPass = 0
    while(True):
        delay_time = 0
        sampledate = datetime.now()
        #counting number of reading times
        sumCnt += 1
        #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
        chk = dht.readDHT11()
    
        # capture temperature in centigrade to be used to calculate dew point
        tempC = dht.temperature
        dht.temperature = dht.temperature *(9/5) +32    
        #print temp and humidity to LCD
        temperature = float("%.2f" % dht.temperature)
        
        if chk == DHTLIB_OK and dht.humidity < 100:
            # NEW DHT2 CODE
            #humidity2, temperature2 = Adafruit_DHT.read_retry(DHT2_SENSOR, DHT2_PIN)
            #if humidity2 is not None and temperature2 is not None:
            #    temperature2 = temperature2 * 9/5 + 32
            #    temperature = temperature2
                #print("DHT22 Temp={0:0.1f}F Humidity={1:0.1f}%".format(temperature2,humidity2))
            #else:
            #    print("Sensor DHT2 failure")
            #    print("DHT11 Temp={0:0.1f}F Humidity={1:0.1f}%".format(temperature,dht.humidity))
            dewPoint = calc_dewpoint(tempC, dht.humidity)
            #dewPoint = dewpoint_approximation(dht.temperature,dht.humidity)
            dewPoint = float("%.2f" % dewPoint)
            prev_dewp = dewPoint
            good_reading +=1
            GPIO.output(ledPin, GPIO.HIGH)  # led on
            if LCD_ENABLED:
                LCD.run_lcd("Temp F ", str(temperature),"Humidity % ", dht.humidity)
            time.sleep(5)
            if dewPoint < 50:
                dewPtext = "ok"
            elif dewPoint > 65:
                dewPtext = "Very High"
            else:
                dewPtext = "High"
            
            if LCD_ENABLED:
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
                #print("Bad Temp Value", temperature, " ", sumCnt)

            if dht.humidity > (hum_average - (hum_average*valueDifferentialMinus)) and dht.humidity < (hum_average*valueDifferentialPlus):
                prev_hum = dht.humidity
            else:
                dht.humidity = prev_hum
                #print("Bad Hum Value",dht.humidity, " ", sumCnt)

            if len(temperature_list) > list_size:
                temperature_list.pop(0)
                humidity_list.pop(0)
                dewp_list.pop.pop(0)
                sampledate_list.pop(0)
                
            temperature_list.extend([temperature])
            humidity_list.extend([dht.humidity])
            dewp_list.extend([dewPoint])
            sampledate_list.extend([sampledate])
            #print('\nTimestamp', sampledate)
            # check if lock file exist since it means file is being updated and we should not access it
            while os.path.isfile('lockplot.txt'):
                time.sleep(1)
                print("lockplot active ",datetime.now())
            #temp file to lock file reader for plotting
            f = open("./lock.txt", 'w')
            with open('./envfile.data', 'wb') as filehandle: 
                # store the data as binary data stream
                pickle.dump(temperature_list, filehandle)
                pickle.dump(humidity_list, filehandle)
                pickle.dump(dewp_list, filehandle)
                pickle.dump(sampledate_list, filehandle)
            f.flush()
            f.close()
            os.remove("./lock.txt")
            #print(f"        Good= {good_reading} Bad={bad_reading} Chk={chk}")
            pctgood = float("%.2f" % ((good_reading/(good_reading+bad_reading)*100)))
            #print('        Percent good', pctgood,'%')
            #print(f"Temp F {temperature}, Humidity {dht.humidity}")
            #time.sleep(1)
            GPIO.output(ledPin, GPIO.LOW) # led off
            # failed reading DHT
        else:
            bad_reading+=1
            #print("DHT11 bad read")
            if chk == -1:
                if LCD_ENABLED:
                    LCD.run_lcd("Bad DHT Read ",str(chk),"DHTLIB_CHECKSUM","")
                #print('DHTLIB_CHECKSUM')
            elif chk == -2:
                if LCD_ENABLED:
                    LCD.run_lcd("Bad DHT Read ",str(chk),"DHTLIB_TIMEOUT","")
                #print('DHTLIB_TIMEOUT')
            else:
                if LCD_ENABLED:
                    LCD.run_lcd("Bad DHT Read ",str(chk),"DHTLIB_INVALID","")
                    time.sleep(2)
                #print('DHTLIB_INVALID')
        while (delay_time < SAMPLE_TIME):
            if GPIO.input(buttonPin)==GPIO.LOW:
                # shutdown box or stop flashing the LED during samples.
                # if the button is clicked, the LED stops flashing
                # if the button is pressed for 10 seconds, the box powers down
                loopCnt=0
                buttonPressed=0
                if LCD_ENABLED:
                    LCD.run_lcd("Confirm Shutdown ","","","")
                    time.sleep(3)
                while(loopCnt < 5):
                    print('Shutdown')
                    GPIO.output(ledPin, GPIO.HIGH)  # led on
                    time.sleep(.2)
                    GPIO.output(ledPin, GPIO.LOW)  # led on
                    time.sleep(.2)
                    loopCnt +=1
                GPIO.cleanup()
                os.system("shutdown now -h")
            time.sleep(1)
            delay_time +=1

        #print("--- %s seconds ---" % (time.time() - start_time))
        if LCD_ENABLED:
            LCD.run_lcd("Time",get_time_now(),"",ipaddr)
            time.sleep(2)
            LCD.run_lcd("Bad ",str(bad_reading)," Good ",str(good_reading))
            time.sleep(2)


        
if __name__ == '__main__':
    #print ('Program is starting ... ')
    try:
        loop()
    except KeyboardInterrupt:
        GPIO.cleanup()
        GPIO.output(ledPin, GPIO.LOW) # Set ledPin low to off led
        exit()  

