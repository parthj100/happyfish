# Import necessary libraries
import os
import time
from datetime import datetime
import board
import busio
from adafruit_pca9685 import PCA9685

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
        self.sunset = os.getenv('SUNSET', '20:56')
        self.duration = int(os.getenv('DURATION', 10))  # duration in minutes
        
        # Convert times to seconds
        self.sunrise_seconds = self.time_to_seconds(self.sunrise)
        self.sunset_seconds = self.time_to_seconds(self.sunset)
        self.duration_seconds = self.duration * 60  # converting minutes to seconds
        
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
    # Set the PWM duty cycle for all channels based on the brightness percentage
    real_duty_cycle = int(duty_cycle * 65535)
    for channel in range(16):  # Assuming 16 channel PWM driver
        pca.channels[channel].duty_cycle = real_duty_cycle

def log_time_brightness(schedule):
    # Log the current time, stage, and brightness level, and set the PWM duty cycle
    while True:
        current_time = datetime.now().isoformat()
        current_stage = schedule.get_stage()
        brightness = schedule.get_brightness_percentage()
        print(f"Time: {current_time} - Stage: {current_stage} - Brightness Level: {brightness:.2%}")
        set_pwm(brightness)
        time.sleep(60)  # Print every 1 minute

# Main program
schedule = Schedule()
try:
    log_time_brightness(schedule)
except KeyboardInterrupt:
    print("Program stopped manually.")
finally:
    pca.deinit()  # Clean up


