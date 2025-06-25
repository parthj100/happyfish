# Import necessary libraries
import os
import time
from datetime import datetime
import board
import busio
from adafruit_pca9685 import PCA9685
import sys
import glob

sys.path.append('../')  

from CQRobot_ADS1115 import ADS1115
from DFRobot_PH import DFRobot_PH

# Define the stages of the day
class Stages:
    pre_sun_rise = 'PRE Sun-Rise'
    sun_rise = 'Sun-Rise'
    lights_on = 'Day-Time'
    sun_set = 'Sun-Set'
    post_sun_set = 'POST Sun-Set'

# Define the schedule class
class Schedule:
    def __init__(self):
        # Initialize schedule with sunrise and sunset times from environment variables
        self.sunrise = os.getenv('SUNRISE', '06:00')
        self.sunset = os.getenv('SUNSET', '18:00')
        self.duration = int(os.getenv('DURATION', 30))  # duration in minutes
        
        self.sunrise_seconds = self.time_to_seconds(self.sunrise)
        self.sunset_seconds = self.time_to_seconds(self.sunset)
        
        self.duration_seconds = self-duration * 60  # converting minutes to seconds
        
    def time_to_seconds(self, time_str):
        # Convert time string to seconds
        hours, minutes = map(int, time_str.split(':'))
        return hours * 3600 + minutes * 60

    def get_stage(self):
        # Get the current stage based on the current time
        now = datetime.now()
        current_seconds = now.hour * 3600 + now.minute * 60 + now.second
        
        if current_seconds < self.sunrise_seconds:
            return Stages.pre_sun_rise
        elif current_seconds < self.sunrise_seconds + self.duration_seconds:
            return Stages.sun_rise
        elif current_seconds < self.sunset_seconds:
            return Stages.lights_on
        elif current_seconds < self.sunset_seconds + self.duration_seconds:
            return Stages.sun_set
        else:
            return Stages.post_sun_set

    def get_brightness_percentage(self):
        # Get the brightness percentage based on the current stage
        current_stage = self.get_stage()
        now = datetime.now()
        current_seconds = now.hour * 3600 + now.minute * 60 + now.second
        if current_stage == Stages.sun_rise:
            return (current_seconds - self.sunrise_seconds) / self.duration_seconds
        elif current_stage == Stages.sun_set:
            return 1 - ((current_seconds - self.sunset_seconds) / self.duration_seconds)
        elif current_stage in [Stages.lights_on]:
            return 1.0
        return 0.0

# Set up the PCA9685 PWM driver
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = 1000

def set_pwm(duty_cycle):
    """ Set PWM duty cycle for all channels based on current time and daylight stage. """
    real_duty_cycle = int(duty_cycle * 65535)
    for channel in range(16):  # Assuming 16 channel PWM driver
        pca.channels[channel].duty_cycle = real_duty_cycle

# Initialize ADS1115 for pH and TDS sensors
ADS1115_REG_CONFIG_PGA_6_144V = 0x00  # 6.144V range = Gain 2/3

ads1115_pH = ADS1115()
ads1115_pH.setAddr_ADS1115(0x49)  # Set I2C address for pH sensor
ads1115_pH.setGain(ADS1115_REG_CONFIG_PGA_6_144V)  # Set gain for pH

ads1115_TDS = ADS1115()
ads1115_TDS.setAddr_ADS1115(0x49)  # Set I2C address for TDS sensor
ads1115_TDS.setGain(ADS1115_REG_CONFIG_PGA_6_144V)  # Set gain for TDS

ph_sensor = DFRobot_PH()
ph_sensor.begin()

# Initialize schedule
schedule = Schedule()

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    with open(device_file, 'r') as f:
        lines = f.readlines()
    return lines

def read_temp():
    while True:
        lines = read_temp_raw()
        if lines and lines[0].strip()[-3:] == 'YES':
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
                return temp_c  # Return Celsius
        time.sleep(0.2)

try:
    # Main program loop
    while True:
        current_time = datetime.now().isoformat()
        current_stage = schedule.get_stage()
        brightness = schedule.get_brightness_percentage()
        print(f"Time: {current_time} - Stage: {current_stage} - Brightness Level: {brightness:.2%}")
        set_pwm(brightness)
        
        real_time_temp = read_temp()  # Real-time temperature in Celsius

        # Read pH
        adc_pH = ads1115_pH.readVoltage(2)  # Ensure reading from channel 0 for pH
        pH_value = ph_sensor.read_PH(adc_pH['r'], real_time_temp) 
        print(f"Real-time Temperature: {real_time_temp:.2f} °C, PH: {pH_value:.2f}")

        # Read TDS
        adc_TDS = ads1115_TDS.readVoltage(1)  # Ensure reading from channel 1 for TDS
        temp = 25.0
        VREF = 5.0
        averageVoltage = adc_TDS['r'] * (VREF / 1024.0)
        compensationCoefficient = 1.0 + 0.02 * (temp - 25.0)
        compensationVoltage = averageVoltage / compensationCoefficient
        tdsValue = (133.42 * compensationVoltage**3 - 255.86 * compensationVoltage**2 +
                    857.39 * compensationVoltage) * 0.5
        print(f"TDS Voltage: {adc_TDS['r']} mV, TDS: {tdsValue:.0f} ppm")

        time.sleep(1.0)  # Sleep for 1 second before next reading

except KeyboardInterrupt:
    print("Script execution was stopped by keyboard interruption.")
    set_pwm(0.0)  # Turn off LEDs
finally:
    pca.deinit()  # Clean up

