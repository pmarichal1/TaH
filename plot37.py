#!/usr/bin/env python3
# -*- coding: utf-8 
import os
import sys
import platform
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import time

print(sys.version_info)
print(platform.python_version())
print(platform.platform())
temp_dev = 2
hum_dev = 5

lock_hit=0
while(1):
    # check if lock file exist since it means file is being updated and we should not access it
    if os.path.isfile('lock.txt'):
        time.sleep(1)
        lock_hit+=1
    else:
        with open('envfile.data', 'rb') as filehandle:  
            # read the data as binary data stream
            temp_list = pickle.load(filehandle)
            hum_list = pickle.load(filehandle)
        print(f"Len Raw Humidity = {len(hum_list)},  Len Raw Temp = {len(temp_list)}")
        temp_elements = np.array(temp_list)
        temp_mean = np.mean(temp_elements, axis=0)
        temp_sd = np.std(temp_elements, axis=0)
        temp_final_list = [x for x in temp_list if (x <= (temp_mean) + (temp_dev * temp_sd))]
        print(f"******TEMP mean = {temp_mean:2.2f}   dev={temp_sd:2.2f} x={temp_mean + (temp_dev * temp_sd):2.2f} y={temp_mean - (temp_dev * temp_sd):2.2f}")
        temp_final_list = [x for x in temp_final_list if (x >= (temp_mean) - (temp_dev * temp_sd))]
        yarr1 = list(range(len(temp_final_list)))

        hum_elements = np.array(hum_list)
        hum_mean = np.mean(hum_elements, axis=0)
        hum_sd = np.std(hum_elements, axis=0)
        hum_final_list = [x for x in hum_list if (x <= hum_mean + (hum_dev * hum_sd))]
        print(f"******HUM  mean = {hum_mean:2.2f}   dev={hum_sd:2.2f}  x={hum_mean + (hum_dev * hum_sd):2.2f} y={hum_mean - (hum_dev * hum_sd):2.2f}")
        hum_final_list = [x for x in hum_final_list if (x >= hum_mean - (hum_dev * hum_sd))]
        yarr = list(range(len(hum_final_list)))
        print(f"Len Filtered Humidity = {len(hum_final_list)},  Len Filtered Temp = {len(temp_final_list)}")
        print(f"Max Humidity = {max(hum_list)}  Min Humidity = {min(hum_list)}")
        print(f"Max Temperature = {max(temp_list)}  Min Temperature = {min(temp_list)}")
        print(f"Last Temperature = {temp_list[-1]}  Last Humidity = {hum_list[-1]}")
        
        plt.xlabel("Time (5s)")
        plt.ylabel("Humidity % and Temp (F)")
        #plt.plot(yarr, hum_final_list, yarr1, temp_final_list)
        plt.plot(yarr, hum_final_list, label='Hum')
        plt.plot(yarr1, temp_final_list, label='Temp')
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.00), shadow=True, ncol=2)
        plt.draw()
        print(f"---Plot graph finish---    Lock hit = {lock_hit}\n")
        plt.ion()
        plt.show()
        time.sleep(6)
        plt.pause(0.0001)
        plt.clf()

