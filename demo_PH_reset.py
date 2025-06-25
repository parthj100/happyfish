import sys
sys.path.append('../')

# Import the DFRobot_PH module
import time

# Import the DFRobot_PH class
from DFRobot_PH import DFRobot_PH

# Create an instance of the DFRobot_PH class
ph = DFRobot_PH()

# Reset the pH sensor
ph.reset()

# Wait for 0.5 seconds
time.sleep(0.5)

# Exit the program with a status code of 1
sys.exit(1)
