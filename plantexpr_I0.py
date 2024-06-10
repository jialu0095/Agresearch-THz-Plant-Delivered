#%%
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

os.chdir('plant_expr_API')
# os.chdir('plant_expr_API\GA66_data')
#%%

def print_mean_I0(I_group, group_name, dB_group, dB_name, times):
    for i in range(0,times):
        I = I_group[i]
        dB = dB_group[i]
        zero_indices = np.where(I == 0)[0]
        I = np.delete(I, zero_indices)
        dB = np.delete(dB, zero_indices)
        I_0 = 10**(dB/10)*I
        I_0_mean = np.mean(I_0)
        print(f'{group_name} day {i+1} mean I_0: ', I_0_mean)

def cal_mean_I0(I_group, group_name, dB_group, dB_name, times):
    I_0_means = []
    for i in range(0,times):
        I = I_group[i]
        dB = dB_group[i]
        zero_indices = np.where(I == 0)[0]
        I = np.delete(I, zero_indices)
        dB = np.delete(dB, zero_indices)
        I_0 = 10**(dB/10)*I
        I_0_mean = np.mean(I_0)
        I_0_means.append(I_0_mean)
    return I_0_means



#%%
times = 3
# load THz data
I_test_plant = [[] for _ in range(times)]
dB_test_plant = [[] for _ in range(times)]

# data file name
species = "GA66"
plant_number = "1"

for i in range(0,times):
    print(i)
    
    I_test_plant[i] = np.loadtxt('I_wet'+str(i+1)+'_'+species + '_' + plant_number + '.csv', delimiter=' ', comments='#')
    dB_test_plant[i] = np.loadtxt('dB_wet'+str(i+1)+'_'+species + '_' + plant_number + '.csv', delimiter=' ', comments='#')

I0_test_plant = cal_mean_I0(I_test_plant, '', dB_test_plant, '', times)
print('I_0: ', I0_test_plant)


# %%
