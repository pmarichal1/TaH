import os
import numpy as np
import pickle
import time

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
        print(f"TEMP {temp_list[-15:]}")
        print(f"Humidity {hum_list[-15:]}")
        temp_elements = np.array(temp_list)
        temp_mean = np.mean(temp_elements, axis=0)
        temp_sd = np.std(temp_elements, axis=0)
        
        hum_elements = np.array(hum_list)
        hum_mean = np.mean(hum_elements, axis=0)
        hum_sd = np.std(hum_elements, axis=0)

        print("*****Len Humidity = {:<03.2f},  Len Temp = {:<3.2f}".format(len(hum_list),len(temp_list)))
        print("*****MaxH = {:<03.2f},  MaxT  = {:<3.2f}".format(max(hum_list), max(temp_list)))
        print("*****MinH = {:<03.2f},  MinT  = {:<3.2f}".format(min(hum_list), min(temp_list)))
        print(f"*****AvgH = {sum(hum_list)/len(hum_list):3.2f},  AvgT = {sum(temp_list)/len(temp_list):3.2f}")
        print(f"*****TEMP mean = {temp_mean:2.2f}   dev={temp_sd:2.2f}  x={temp_mean + (.5 * temp_sd):2.2f}  y={temp_mean - (.5 * temp_sd):2.2f}")
        print(f"*****HUM  mean = {hum_mean:2.2f}   dev={hum_sd:2.2f}  x={hum_mean + (.5 * hum_sd):2.2f}  y={hum_mean - (.5 * hum_sd):2.2f}")
        print('\n')
        time.sleep(10)