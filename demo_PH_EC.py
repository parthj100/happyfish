import sys
import time
import os
import glob

# Modifying the system path might not be required if the module can be properly installed
sys.path.append('../')

# Importing ADS1115 and sensor interfaces
from CQRobot_ADS1115 import ADS1115
from DFRobot_EC import DFRobot_EC
from DFRobot_PH import DFRobot_PH

# ADS1115 Gain Settings (select the appropriate gain)
ADS1115_REG_CONFIG_PGA_6_144V = 0x00  # 6.144V range = Gain 2/3

# Initialize the ADS1115
ads1115 = ADS1115()
ec = DFRobot_EC()
ph = DFRobot_PH()

# Load required 1-wire GPIO module
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]  # Adjust as per your sensor ID
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    with open(device_file, 'r') as f:
        lines = f.readlines()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

# Initialize sensors
ec.begin()
ph.begin()

# Set the I2C address (if necessary) and gain for the ADS1115
ads1115.setAddr_ADS1115(0x49)
ads1115.setGain(ADS1115_REG_CONFIG_PGA_6_144V)

while True:
    # Read the current temperature
    temperature = read_temp()

    # Read voltages from the ADS1115
    adc0 = ads1115.readVoltage(0)  # pH value reading from channel 0
    adc1 = ads1115.readVoltage(1)  # EC value reading from channel 1

    # Convert voltage to EC and pH with temperature compensation
    EC = ec.readEC(adc1['r'], temperature)
    PH = ph.read_PH(adc0['r'], temperature)

    print(f"Temperature: {temperature:.1f} °C, EC: {EC:.2f} ms/cm, PH: {PH:.2f}")
    time.sleep(1.0)

