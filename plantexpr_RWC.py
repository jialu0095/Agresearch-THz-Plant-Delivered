#%% import libraries and set working directory
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import uncertainties.unumpy as unumpy

'''
set data file directory under 'plant_expr_API/{datafile_folder_name}'
if you have already run this cell, don't run this again
or restart the kernel to choose another data file folder
'''

# os.chdir('plant_expr_API/One50_data')
os.chdir('plant_expr_API/GA66_data')
# os.chdir('plant_expr_API')

#%% functions
# output: dH20(mm)
dH20_unit = 'mm'
def calculate_dH20_plant(I_ref, I_smp, dB_ref, dB_smp, group):
    # ref group: dry plants, smp group: wet plnats

    # remove empty pixels
    zero_indices = np.where((I_ref == 0) | (I_smp == 0))[0]
    print('empty pixels: ', len(zero_indices))
    I_ref = np.delete(I_ref, zero_indices)
    I_smp = np.delete(I_smp, zero_indices)
    dB_ref = np.delete(dB_ref, zero_indices)
    dB_smp = np.delete(dB_smp, zero_indices)

    # get std value to add uncertainty
    I_std_ref = np.std(I_ref)
    I_std_smp = np.std(I_smp)
    dB_std_ref = np.std(dB_ref)
    dB_std_smp = np.std(dB_smp)

    # add uncertainty
    I_ref = unumpy.uarray(I_ref, [I_std_ref]*len(I_ref))
    I_smp = unumpy.uarray(I_smp, [I_std_smp]*len(I_smp))
    dB_ref = unumpy.uarray(dB_ref, [dB_std_ref]*len(dB_ref))
    dB_smp = unumpy.uarray(dB_smp, [dB_std_smp]*len(dB_smp))

    # get mean value
    I_mean_ref = np.mean(I_ref)
    I_mean_smp = np.mean(I_smp)
    dB_mean_ref = np.mean(dB_ref)
    dB_mean_smp = np.mean(dB_smp)
    
    # calculate dH20
    dH20 = (unumpy.log(I_mean_ref / I_mean_smp) + 0.1*unumpy.log(10) * (dB_mean_ref - dB_mean_smp)) / 85 # cm
    dH20 *= 10 # cm to mm
    # mm to um
    if dH20_unit == 'um':
        dH20 *= 1000

    # remove -inf nan values
    # valid_values_mean = np.nanmean(np.where(dH20 == -np.inf, np.nan, dH20))
    # dH20 = np.where(np.isneginf(dH20) | np.isnan(dH20), valid_values_mean, dH20)

    return dH20

# I_0 = 10^(dB/10) * I
# print mean I_0 for each group
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

# calculate mean I_0 for each group
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


# load THz data from csv filess
# attenuation(dB), intensity(I)
def load_THz_data(species, plant_number, times):
    I = [[] for _ in range(times)]
    dB = [[] for _ in range(times)]
    for i in range(0,times):
        I[i] = np.loadtxt('I_wet' + str(i+1) + '_' + species + '_' + plant_number + '.csv', delimiter=' ', comments='#')
        dB[i] = np.loadtxt('dB_wet' + str(i+1) + '_' + species + '_' + plant_number + '.csv', delimiter=' ', comments='#')
    return I, dB

# calculate dH20 for all dry times
def cal_all_dH20(I, dB, times):
    dH20 = [[] for _ in range(times)]
    for i in range(0,times):
        dH20[i] = calculate_dH20_plant(I[-1], I[i], dB[-1], dB[i], i+1)
    return dH20

# calculate RWC_THz
def cal_RWC_THz(dH20, dH20_max):
    RWC_THz = [d / dH20_max for d in dH20]
    return RWC_THz

# calculate adjusted nominal values and standard deviation 
def calculate_adjusted_nominal_std(RWC_THz, RWC_gravimetric):
    # get nominal values
    RWC_THz_nominal = unumpy.nominal_values(RWC_THz)
    
    #calculate the additional error factor
    additional_error_factor = abs(RWC_gravimetric[0] - RWC_THz_nominal[0]) / RWC_THz_nominal[0]
    
    # calculate standard deviation and adjust it
    RWC_THz_adjusted_std = unumpy.std_devs(RWC_THz) * (1 + additional_error_factor)
    
    # set the standard deviation of the last element to 0
    RWC_THz_adjusted_std[-1] = 0
    
    return RWC_THz_nominal, RWC_THz_adjusted_std


# all in one functions
def THz_results(species, plant_number, times):
    I, dB = load_THz_data(species, plant_number, times)
    dH20 = cal_all_dH20(I, dB, times)
    RWC_THz = cal_RWC_THz(dH20, dH20[0])
    print(f'{species}-{plant_number} RWC_THz: ', RWC_THz)
    # return RWC_THz
    return RWC_THz

# run single experiment
def run_single_experiment(plant_id, experiment_id, times, gravimetric_data):
    # Retrieve THz measurement results for the specified experiment
    thz_results = THz_results(plant_id, experiment_id, times)
    
    # Calculate adjusted nominal values and standard deviations
    nominal, std = calculate_adjusted_nominal_std(thz_results, gravimetric_data)
    
    # Return nominal and standard deviation directly
    return nominal, std

# plot single experiment
def plot_rwc_data(x_values, rwc_gravimetric, rwc_thz_nominal, rwc_thz_std, title, xlabel):
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.suptitle('RWC_THz for Each Group')

    # Plot gravimetric data
    ax.scatter(x_values, rwc_gravimetric, marker='o', color='red', label='RWC_gravimetric')

    # Plot THz data with error bars
    ax.errorbar(x_values, rwc_thz_nominal, yerr=rwc_thz_std, fmt='o', label='RWC_THz', capsize=5)

    # Set the title and labels for the plot
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel('RWC_THz [%]')
    ax.legend()

    # Display the plot
    plt.show()

# %% GA66_1 and GA66_2 THz&gravimetric RWC results

plant_id = 'GA66'   # plant breed
times = 8   # number of dry times

# Define experiment parameters for the first experiment
experiment_id_1 = '1'
RWC_gravimetric_GA66_1 = [0.978070175, 0.936090226, 0.974576271, 0.883802817, 0.821917808, 0.746153846, 0, 0]

# Run experiment for the first ID
RWC_THz_GA66_1_nominal, RWC_THz_GA66_1_std = run_single_experiment(plant_id, experiment_id_1, times, RWC_gravimetric_GA66_1)
print(f"Results for {plant_id}_{experiment_id_1}: Nominal - {RWC_THz_GA66_1_nominal}, Std - {RWC_THz_GA66_1_std}")

# Define parameters for the second experiment
experiment_id_2 = '2'
RWC_gravimetric_GA66_2 = [0.988095238, 0.97761194, 0.965909091, 0.935185185, 0.888888889, 0.810810811, 0, 0]

# Run experiment for the second ID
RWC_THz_GA66_2_nominal, RWC_THz_GA66_2_std = run_single_experiment(plant_id, experiment_id_2, times, RWC_gravimetric_GA66_2)
print(f"Results for {plant_id}_{experiment_id_2}: Nominal - {RWC_THz_GA66_2_nominal}, Std - {RWC_THz_GA66_2_std}")

#%% plot RWC data with functions
# Define the x-axis values and plot parameters
times = 8   # number of dry times
x_values = range(1, times + 1)  # x-axis values (dry times points)
xlabel = 'Time [/20mins]'   # x-axis label

# plot the RWC data
plot_rwc_data(x_values, RWC_gravimetric_GA66_1, RWC_THz_GA66_1_nominal, RWC_THz_GA66_1_std, 'Plant GA66-1', xlabel)

# Define the x-axis values and plot parameters
times = 8
x_values = range(1, times + 1)
xlabel = 'Time [/20mins]'
# plot the RWC data
plot_rwc_data(x_values, RWC_gravimetric_GA66_2, RWC_THz_GA66_2_nominal, RWC_THz_GA66_2_std, 'Plant GA66-2', xlabel)

#%% self-define plots
x_values = range(1, times + 1)

# Plotting RWC_THz for each group with error bars
fig, axs = plt.subplots(2, 1, figsize=(12, 12))
fig.suptitle('RWC_THz for Each Group')

dry_time_gap = '/20mins'
# Plot for GA66-1 with error bars
axs[0].scatter(range(1, times+1), RWC_gravimetric_GA66_1, marker='o', color='red', label='RWC_gravimetric')
axs[0].errorbar(x_values, RWC_THz_GA66_1_nominal, yerr=RWC_THz_GA66_1_std, fmt='o', label='RWC_THz', capsize=5)
axs[0].set_title('Plant GA66-1')
axs[0].set_xlabel('Time [/20mins]')
axs[0].set_ylabel('RWC_THz [%]')
axs[0].legend()

# Plot for GA66-2 with error bars
axs[1].scatter(range(1, times+1), RWC_gravimetric_GA66_2, marker='o', color='red', label='RWC_gravimetric')
axs[1].errorbar(x_values, RWC_THz_GA66_2_nominal, yerr=RWC_THz_GA66_2_std, fmt='o', label='RWC_THz', capsize=5)
axs[1].set_title('Plant GA66-2')
axs[1].set_xlabel('Time [/20mins]')
axs[1].set_ylabel('RWC_THz [%]')
axs[1].legend()

plt.tight_layout()
plt.show()

# %%
