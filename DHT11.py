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
import Blink
import LCD
import pickle
from datetime import datetime

# time function
DHTPin = 15     #define the pin of DHT11

def get_time_now():     # get system time
    return datetime.now().strftime(' %H:%M:%S')

def get_date_now():     # get system time
    return datetime.now().strftime('%A %B %D   %H:%M:%S')

# main loop
def loop():
    dht = DHT.DHT(DHTPin)   #create a DHT class object
    sumCnt = 0              #number of reading times
    Blink.setup_led()
    hi_temp = 0
    low_temp = 150
    hi_hum = 0
    low_hum = 110
    bad_reading=0
    temperature_list = []
    humidity_list = []
    list_size = 200
    distance=0
    while(True):
        print(get_date_now())
        sumCnt += 1         #counting number of reading times
        chk = dht.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
        print(" Length of list %d"%(len(temperature_list)))
        #print(len(temperature_list))
        print ("The Loop Count  is : %d, \t chk    : %d"%(sumCnt,chk))
        if (chk is dht.DHTLIB_OK):      #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
            print("DHT11,OK!")
        elif(chk is dht.DHTLIB_ERROR_CHECKSUM): #data check has errors
            print("DHTLIB_ERROR_CHECKSUM!!")
        elif(chk is dht.DHTLIB_ERROR_TIMEOUT):  #reading DHT times out
            print("DHTLIB_ERROR_TIMEOUT!")
        else:               #other errors
            print("Other error!")
        dht.temperature = dht.temperature *(9/5) +32    
        #print temp and humidity to LCD
        temperature = float("%.2f" % dht.temperature)
        #if temperature > 0 and dht.humidity > 0:
        if chk == 0:
            LCD.run_lcd("Temp F ", str(temperature),"Humidity % ", dht.humidity)
            Blink.flash_led()
            if len(temperature_list) > list_size:
                temperature_list.pop(0)
                humidity_list.pop(0)
            temperature_list.extend([temperature])
            humidity_list.extend([dht.humidity])
            temp_average = sum(temperature_list) / len(temperature_list)
            hum_average = sum(humidity_list) / len(humidity_list) 

            #temp file to lock file reader for plotting
            f = open("lock.txt", 'w')
            with open('envfile.data', 'wb') as filehandle:  
                # store the data as binary data stream
                pickle.dump(temperature_list, filehandle)
                pickle.dump(humidity_list, filehandle)
                pickle.dump(distance, filehandle)
            f.close()
            os.remove("lock.txt")
            # need to compensate for bad numbers so can't increase or decrease more than 15% in one sample
            if temperature > hi_temp and temperature < (temp_average*1.15):
                hi_temp = temperature
            if temperature < low_temp and temperature > (temp_average - (temp_average*.15)):
                low_temp = temperature
            if dht.humidity > hi_hum and dht.humidity < (hum_average*1.15):
                hi_hum = dht.humidity
            if dht.humidity < low_hum and dht.humidity > (hum_average - (hum_average*.15)):
                low_hum = dht.humidity
            print("Current Humidity :     %.2f, \t Current Temperature :     %.2f"%(dht.humidity, temperature))
            print("Average Humidity :     %.2f, \t Average Temperature :     %.2f"%(hum_average, temp_average))
            print("Hi Humidity :          %.2f, \t Hi Temperature :          %.2f"%(hi_hum, hi_temp))
            print("Low Humidity :         %.2f, \t Low Temperature :         %.2f"%(low_hum, low_temp))
        else:
            bad_reading+=1


        #print(temperature_list)
        #print(humidity_list) 
        print("Bad reads = %d %%\n"%((bad_reading/sumCnt)*100))
        time.sleep(3)
        LCD.run_lcd("Time",get_time_now())
        time.sleep(3)

        
if __name__ == '__main__':
    print ('Program is starting ... ')
    try:
        loop()
    except KeyboardInterrupt:
        GPIO.cleanup()
        Blink.destroy_led()
        exit()  

