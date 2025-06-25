# Import necessary libraries
import time
import board
import busio
from adafruit_pca9685 import PCA9685

# Create the I2C bus interface
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = 1000  # Set the frequency for PWM

# Define a function to set the PWM duty cycle for a single channel
def set_pwm(channel, duty_cycle):
    """ Set PWM duty cycle for a single channel. """
    pca.channels[channel].duty_cycle = duty_cycle

# Define a function to calculate the brightness percentage
def brightness_percentage(duty_cycle):
    """ Calculate and return the brightness percentage. """
    return (duty_cycle / 65535) * 100

# Define a function to gradually adjust brightness for all 12 LEDs
def adjust_leds_brightness(duration=5, step=10, up=True):
    """ Gradually adjust brightness for all 12 LEDs over the specified duration. """
    step_size = 65535 // (duration * 100 // step)
    range_function = range(0, 65536, step_size) if up else range(65535, -1, -step_size)
    total_seconds = duration * 60
    sleep_time = total_seconds / len(range_function)
    
    for brightness in range_function:
        for channel in range(12):
            set_pwm(channel, brightness)
        time.sleep(sleep_time)  # Delay to mimic natural sunrise/sunset
        print(f"Brightness: {brightness_percentage(brightness):.2f}%")

# Define a function for interactive control to simulate sunrise and sunset
def simulate_light():
    while True:
        user_input = input("Enter 'sunrise', 'sunset', or 'exit': ").strip().lower()
        if user_input == "sunrise":
            print("Simulating sunrise...")
            adjust_leds_brightness(up=True)
        elif user_input == "sunset":
            print("Simulating sunset...")
            adjust_leds_brightness(up=False)
        elif user_input == "exit":
            print("Exiting program.")
            break
        else:
            print("Invalid input, please enter 'sunrise', 'sunset', or 'exit'.")

# Main program
try:
    simulate_light()
except KeyboardInterrupt:
    print("Program stopped manually.")
finally:
    # Clean up to turn off PWM signal
    pca.deinit()
