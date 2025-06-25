import sys
sys.path.append('../')
import time

# Import the DFRobot_EC module
from DFRobot_EC import DFRobot_EC

# Create an instance of the DFRobot_EC class
ec = DFRobot_EC()

# Reset the EC sensor
ec.reset()

# Wait for 0.5 seconds
time.sleep(0.5)

# Exit the program with a status code of 1
sys.exit(1)
