# THz System Manual

# Packages Installation

Unzip the file

Go into folder `/THz Camera packages` 

## Python installation

Run batch file `install.bat` by double clicking it. (if you already have python 3.x installed, ignore this step)

## Pip installation

(if you already have `pip` installed, ignore this step. run `pip` in the command line to test)

Download pip from [https://bootstrap.pypa.io/get-pip.py](https://bootstrap.pypa.io/get-pip.py)

And then run

```jsx
python get-pip.py
```

## Python libraries

Run the command below in terminal/command line:

```python
pip install numpy matplotlib pyserial pandas uncertainties
```

## Terasense software

1. Run the command below in the command line in directory `/THz Camera packages`:

```jsx
pip3 install Terasense-4.0.1-py3-none-any.whl
```

1. Install driver for the device controller by clicking `FrontPanelUSB-DriverOnly-5.0.2.exe` , the .exe file is in `/THz Camera packages/driver`
   
    ![Untitled](THz%20System%20Manual%200d2fe8c169dc4ca4b82eec44b939f44e/Untitled.png)
    
2. Then find the software file `TSV.pyw` in `Python3x\Scripts\TSV.pyw` or `Anaconda\Scripts\TSV.pyw`. And make a shortcut for the file by simply copy it in your working directory.
   
    ![Untitled](THz%20System%20Manual%200d2fe8c169dc4ca4b82eec44b939f44e/Untitled%201.png)
    

# Script and Software Usage

## Terasense software

Connect the camera to the computer and double click `TSV.pyw` to launch the software.

![Untitled](THz%20System%20Manual%200d2fe8c169dc4ca4b82eec44b939f44e/Untitled%202.png)

There are 32*32 pixels in the screen. 

red yellow green: high pixel value

blue black: low pixel value

## thz_source_adjust.py

This script is for adjusting the attenuation of the terasense source.

This script can only be working when the computer is connected to the terasense source.

1. Open **device manager** from control panel
2. Search for **port** and check which port is connected to the source. (usually COM3 or COM4)
3. Set the `COM_port` to your port number. ( COM{?} )

e.g. Adjust the attenuation to 6dB:

```python
serialPort.write(b':OUTP:ATT 6\r') 
```

## thz_plantexpr_getAPIdata.py

This script is for collecting plant THz data for every dry time for every plant.

Every time two files saved: dB_plant(attenuation), I_plant(intensity)

1. Set the directory where you want to save the data files

```python
os.chdir('plant_expr_API')
```

1. Set your COM port (e.g. COM3)

```python
COM_port = 'COM3'
```

1. Set the data file name

```python
# data file name
test_group = 'wet'
group_number = "3"
plant_label = "test"
title = test_group + group_number + '_' + plant_label
```

1. Set the working area (take scan of whole screen by default)

```python
# data file name
test_group = 'wet'
group_number = "3"
plant_label = "test"
title = test_group + group_number + '_' + plant_label
```

Run the python file to collect the data. When you see the output `data saved!` , that means the data is collected successfully.

Notice: remember to close `TSV.pyw` before running this script.

## plantexpr_RWC.py

This script is for calculating RWC(relative water content) with THz data and gravimetric data.
1. Ensure your data files are properly organized under the directory `plant_expr_API/`. Create a specific folder within this directory for each dataset (e.g., `One50_data`, `GA66_data`).

1. Use the function `run_single_experiment` to execute an experiment, providing the plant ID, experiment ID, number of time points, and gravimetric data. This function handles the entire process, from data loading to RWC calculation and nominal value adjustment. The return variable is THz RWC nominal value and THz RWC std.

```python

plant_id = 'GA66'   # plant breed
times = 8   # number of dry times

# Define experiment parameters for the first experiment
experiment_id_1 = '1'
RWC_gravimetric_GA66_1 = [0.978070175, 0.936090226, 0.974576271, 0.883802817, 0.821917808, 0.746153846, 0, 0]

# Run experiment for the first ID
RWC_THz_GA66_1_nominal, RWC_THz_GA66_1_std = run_single_experiment(plant_id, experiment_id_1, times, RWC_gravimetric_GA66_1)
print(f"Results for {plant_id}_{experiment_id_1}: Nominal - {RWC_THz_GA66_1_nominal}, Std - {RWC_THz_GA66_1_std}")
```

1. Use the provided `plot_rwc_data` to visualize RWC data. The function accepts time points, RWC data (gravimetric and THz), and plot labels.

```python
times = 8   # number of dry times
x_values = range(1, times + 1)  # x-axis values (dry times points)
xlabel = 'Time [/20mins]'   # x-axis label

# plot the RWC data
plot_rwc_data(x_values, RWC_gravimetric_GA66_1, RWC_THz_GA66_1_nominal, RWC_THz_GA66_1_std, 'Plant GA66-1', xlabel)
```

## plantexpr_I0.py

This script is to check how the data looks like in the middle of the experiment through I_0. (I_0 = 10^(dB/10)*intensity) 

Change `times` to current dry time. e.g. now is the 7th dry time:
```python
times = 7
```

Set the file name

```python
# data file name
test_group = 'wet'
group_number = "3"
plant_label = "test"
```



## Important Notes

- Modify and review the script carefully when changing datasets or plant species to ensure the paths and data file names match those in your directory.
- Keep backups of original data to avoid accidental data loss during script execution or kernel restarts.

# Experiment Process

![Untitled](THz%20System%20Manual%200d2fe8c169dc4ca4b82eec44b939f44e/Untitled%203.png)