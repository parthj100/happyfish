import sys
sys.path.append('../')

import time
from CQRobot_ADS1115 import ADS1115
from DFRobot_PH import DFRobot_PH

# ADS1115 register configuration for different voltage ranges
ADS1115_REG_CONFIG_PGA_6_144V        = 0x00 # 6.144V range = Gain 2/3
ADS1115_REG_CONFIG_PGA_4_096V        = 0x02 # 4.096V range = Gain 1
ADS1115_REG_CONFIG_PGA_2_048V        = 0x04 # 2.048V range = Gain 2 (default)
ADS1115_REG_CONFIG_PGA_1_024V        = 0x06 # 1.024V range = Gain 4
ADS1115_REG_CONFIG_PGA_0_512V        = 0x08 # 0.512V range = Gain 8
ADS1115_REG_CONFIG_PGA_0_256V        = 0x0A # 0.256V range = Gain 16

# Initialize the ADS1115 module
ads1115 = ADS1115()

# Initialize the DFRobot_PH module
ph = DFRobot_PH()

# Initialize the pH sensor
ph.begin()

# Set the number of calibrations
calibration_count = 0
max_calibrations = 5  # Example: limiting the loop to 30 iterations

# Calibration loop
while calibration_count < max_calibrations:
    # Set the temperature for temperature compensation
    temperature = 25  # Read your temperature sensor to execute temperature compensation
    
    # Set the I2C address
    ads1115.setAddr_ADS1115(0x49)
    
    # Set the input voltage range
    ads1115.setGain(ADS1115_REG_CONFIG_PGA_6_144V)
    
    # Read the voltage from channel 0
    adc0 = ads1115.readVoltage(0)
    print(f"A0: {adc0['r']} mV")
    
    # Perform pH calibration
    ph.calibration(adc0['r'])
    calibration_count += 1
    time.sleep(1.0)

print(f"Completed {calibration_count} calibration cycles.")
