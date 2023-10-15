 ##################################################

#           P26 ----> Relay_Ch1
#			P20 ----> Relay_Ch2
#			P21 ----> Relay_Ch3

##################################################
#!/usr/bin/python
# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
import time

Relay_Ch1 = 26
Relay_Ch2 = 20
Relay_Ch3 = 21
sleep_time=3

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(Relay_Ch1,GPIO.OUT)
GPIO.setup(Relay_Ch2,GPIO.OUT)
GPIO.setup(Relay_Ch3,GPIO.OUT)

print("Setup The Relay Module is [success]")

try:
	while True:
		#Control the Channel 1
		GPIO.output(Relay_Ch1,GPIO.LOW)
		print("Channel Blue:The Common Contact is access to the Normal Open Contact!")
		time.sleep(sleep_time)
	
		GPIO.output(Relay_Ch1,GPIO.HIGH)
		print("Channel Blue:The Common Contact is access to the Normal Closed Contact!\n")
		time.sleep(sleep_time)

		#Control the Channel 2
		GPIO.output(Relay_Ch2,GPIO.LOW)
		print("Channel Red:The Common Contact is access to the Normal Open Contact!")
		time.sleep(sleep_time)
		
		GPIO.output(Relay_Ch2,GPIO.HIGH)
		print("Channel Red:The Common Contact is access to the Normal Closed Contact!\n")
		time.sleep(sleep_time)

		#Control the Channel 3
		GPIO.output(Relay_Ch3,GPIO.LOW)
		print("Channel Green:The Common Contact is access to the Normal Open Contact!")
		time.sleep(sleep_time)
		
		GPIO.output(Relay_Ch3,GPIO.HIGH)
		print("Channel Green:The Common Contact is access to the Normal Closed Contact!\n")
		time.sleep(sleep_time)
		
except:
	print("except")
	GPIO.cleanup()
