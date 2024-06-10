import numpy as np
import matplotlib.pyplot as plt
from terasense import processor
import terasense.worker
import serial
import os

# change working dir
os.chdir('plant_expr_API')
print(os.getcwd())

# COM port for the source
COM_port = 'COM3'

# data file name
group_number = "3"
species = "GA66"
plant_number = "1"
title = 'wet' + group_number + '_' + species + "_" + plant_number

# set the working area
x_left = 0
x_right = 31
y_top = 0
y_bottom = 31

def set_attenuation(serialPort, attenuation):
    serialPort.write(b':OUTP:ATT ' + str(attenuation).encode() + b'\r')

def query_attenuation(serialPort):
    serialPort.write(b':OUTP:ATT?\r')
    res = serialPort.read(100)
    attenuation_value = float(res.decode().strip())
    return attenuation_value

def print_attenuation(attenuation_value):
    print("Current Attenuation:", attenuation_value, "dB")

def cal_I0(attenuation_value, pixel_value):
    return 10**(attenuation_value/10)*pixel_value

# open the serial port
serialPort = serial.Serial(port=COM_port, baudrate=115200, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
print(f'{COM_port} is open:', serialPort.isOpen())
serialPort.write(b':OUTP:ATT?\r')   # query the attenuation
res = serialPort.read(100)  # read response

# proc instance
proc = processor.processor(threaded=False)

# worker instance
worker = terasense.worker.Worker()
worker.SetGamma(1)

x_shape = x_right - x_left + 1
y_shape = y_bottom - y_top + 1


# pixel number in the working area
n_pixels = (x_right - x_left + 1) * (y_bottom - y_top  + 1)

# variables
alphas = []
I_0_threshold = 4.95957
saturated_threshold = 0.5
attenuation_step = 0.1
start_attenuation_value = 14

I_sat = [-1] * n_pixels
dB_sat = [-1] * n_pixels
pix_is_sat = [False] * n_pixels
pix_is_empty = [False] * n_pixels


# below code collects THz data
try:
    print("-----------------------------------")

    # set initail attenuation
    attenuation_value = start_attenuation_value
    set_attenuation(serialPort, attenuation_value)
    attenuation_value = query_attenuation(serialPort)
    print_attenuation(attenuation_value)

    data = proc.read()
    data_working = data[x_left:(x_right+1), y_top:(y_bottom+1)].flatten()

    # initial scan
    for index, pixel in enumerate(data_working):
        if pixel > saturated_threshold and pix_is_sat[index] == False:
            I_sat[index] = pixel
            dB_sat[index] = attenuation_value
            pix_is_sat[index] = True 

    # decrease attenuation
    while True:
        # data before altering attenuation
        data_pre = proc.read()
        data_working_pre = data_pre[x_left:(x_right+1), y_top:(y_bottom+1)].flatten()

        # decrease attenuation
        set_attenuation(serialPort, attenuation_value - attenuation_step)
        attenuation_value = query_attenuation(serialPort)
        print_attenuation(attenuation_value)

        # data after altering attenuation
        data = proc.read()
        data_working = data[x_left:(x_right+1), y_top:(y_bottom+1)].flatten()

        # check for saturated pixels
        for index, pixel in enumerate(data_working):
            if (pixel > saturated_threshold) and pix_is_sat[index] == False:
                I_0 = cal_I0(attenuation_value, pixel)
                if I_0 < I_0_threshold:
                    I_sat[index] = pixel
                    dB_sat[index] = attenuation_value
                else:
                    print(I_0)
                    I_sat[index] = 0
                    dB_sat[index] = attenuation_value
                pix_is_sat[index] = True 

        # set the decreased attenuation for next loop
        attenuation_value -= attenuation_step

        # check how many un-saturated pixel left
        false_count = pix_is_sat.count(False)
        print("Number of False in pix_is_sat:", false_count)
        if all(pix_is_sat):
            break

        # for pixel that are still not saturated at 0.1 dB, record current pixel value
        if(attenuation_value <= 0.1):
            for index, pixel in enumerate(pix_is_sat):
                if pixel == False:
                    I_sat[index] = data_working[index]
                    dB_sat[index] = attenuation_value
                    pix_is_sat[index] = True 
            break


    # save data files
    np.savetxt(f'I_{title}.csv', I_sat, fmt='%f')
    np.savetxt(f'dB_{title}.csv', dB_sat, fmt='%f')
    print("data saved")
    
except ValueError:
    print("Error: ", ValueError)
    print("Error reading attenuation value:", res.decode().strip())
finally:
    set_attenuation(serialPort, 14)

# close the serial port
serialPort.close()