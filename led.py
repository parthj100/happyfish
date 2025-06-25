import time
import board
import busio
from adafruit_pca9685 import PCA9685

# Create the I2C bus interface
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = 1000  # Set the frequency for PWM

def set_pwm(channel, duty_cycle):
    """ Set PWM duty cycle for a single channel. """
    pca.channels[channel].duty_cycle = duty_cycle

def brightness_percentage(duty_cycle):
    """ Calculate and return the brightness percentage. """
    return (duty_cycle / 65535) * 100

def adjust_leds_brightness(up=True):
    """ Adjust brightness for all 12 LEDs, either up or down. """
    step = 256  # Step size for brightness change
    range_function = range(0, 65536, step) if up else range(65535, -1, -step)
    for brightness in range_function:  # Control brightness incrementally
        for channel in range(12):  # Control all 12 channels
            set_pwm(channel, brightness)
            print(f"Channel {channel} brightness: {brightness_percentage(brightness):.2f}%")
        if up:
            time.sleep(0.01)  # Delay to see the brightness change

# Interactive control for turning LEDs on or off
def control_leds():
    while True:
        user_input = input("Enter 'on', 'off', or 'exit': ").strip().lower()
        if user_input == "on":
            print("Turning LEDs on...")
            adjust_leds_brightness(up=True)
            print("Do you want to dim the lights now?")
            dim_input = input("Enter 'yes' to dim, any other key returns to main menu: ").strip().lower()
            if dim_input == "yes":
                adjust_leds_brightness(up=False)
        elif user_input == "off":
            print("Turning LEDs off...")
            for channel in range(12):
                set_pwm(channel, 0)
            print("All LEDs are turned off.")
        elif user_input == "exit":
            print("Exiting program.")
            break
        else:
            print("Invalid input, please enter 'on', 'off', or 'exit'.")

try:
    control_leds()
except KeyboardInterrupt:
    print("Program interrupted manually.")
finally:
    # Clean up to turn off PWM signal
    pca.deinit()

