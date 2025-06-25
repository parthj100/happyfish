import os
import glob
import time

# Load kernel modules for 1-wire GPIO and thermocouple
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# Set the base directory for 1-wire devices
base_dir = '/sys/bus/w1/devices/'

# Find the folder for the first device with ID starting with '28'
device_folder = glob.glob(base_dir + '28*')[0]

# Set the file path for the temperature sensor data
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    # Open the temperature sensor file and read its content
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    # Read the temperature sensor data
    lines = read_temp_raw()

    # Wait until the data is valid (last three characters of the first line should be 'YES')
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()

    # Extract the temperature value from the second line
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f

# Continuously print the temperature in Celsius and Fahrenheit every 5 seconds
while True:
    print(read_temp())
    time.sleep(5)