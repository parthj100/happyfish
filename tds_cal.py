import sys
sys.path.append('../')
import time
from CQRobot_ADS1115 import ADS1115

ADS1115_REG_CONFIG_PGA_6_144V = 0x00  # 6.144V range = Gain 2/3
ADS1115_REG_CONFIG_PGA_4_096V = 0x02  # 4.096V range = Gain 1
ADS1115_REG_CONFIG_PGA_2_048V = 0x04  # 2.048V range = Gain 2 (default)
ADS1115_REG_CONFIG_PGA_1_024V = 0x06  # 1.024V range = Gain 4
ADS1115_REG_CONFIG_PGA_0_512V = 0x08  # 0.512V range = Gain 8
ADS1115_REG_CONFIG_PGA_0_256V = 0x0A  # 0.256V range = Gain 16

ads1115 = ADS1115()
# Set the I2C address
ads1115.setAddr_ADS1115(0x49)
# Sets the gain and input voltage range.
ads1115.setGain(ADS1115_REG_CONFIG_PGA_6_144V)

VREF = 5.0
analogBuffer = [0] * 30
analogBufferTemp = [0] * 30
analogBufferIndex = 0
averageVoltage = 0
tdsValue = 0
temperature = 25

calibration_mode = False
calibration_value = 0

def getMedianNum(iFilterLen):
    global analogBufferTemp
    for j in range(iFilterLen - 1):
        for i in range(iFilterLen - j - 1):
            if analogBufferTemp[i] > analogBufferTemp[i + 1]:
                analogBufferTemp[i], analogBufferTemp[i + 1] = analogBufferTemp[i + 1], analogBufferTemp[i]
    
    if iFilterLen & 1 > 0:
        bTemp = analogBufferTemp[(iFilterLen - 1) // 2]
    else:
        i = iFilterLen // 2
        bTemp = (analogBufferTemp[i] + analogBufferTemp[i - 1]) / 2.0
    
    return float(bTemp)

analogSampleTimepoint = time.time()
printTimepoint = time.time()
while True:
    if time.time() - analogSampleTimepoint > 0.04:
        analogSampleTimepoint = time.time()
        analogBuffer[analogBufferIndex] = ads1115.readVoltage(1)['r']
        analogBufferIndex = (analogBufferIndex + 1) % 30

    if time.time() - printTimepoint > 0.8:
        printTimepoint = time.time()
        for copyIndex in range(30):
            analogBufferTemp[copyIndex] = analogBuffer[copyIndex]
        medianVoltage = getMedianNum(30)
        print(" A1:%dmV " % medianVoltage)

        if calibration_mode:
            # Calibration mode is active
            if calibration_value > 0:
                # Calibrate with the known TDS value
                averageVoltage = medianVoltage * (VREF / 1024.0)
                compensationCoefficient = 1.0 + 0.02 * (temperature - 25.0)  # Temperature compensation
                compensationVoltage = averageVoltage / compensationCoefficient
                tdsValue = (133.42 * compensationVoltage**3 - 255.86 * compensationVoltage**2 + 857.39 * compensationVoltage) * 0.5
                print(" Calibrated TDS value: %d ppm" % calibration_value)
                calibration_mode = False
            else:
                print(" Enter calibration value (e.g., cal:707): ")
                user_input = input()
                if user_input.startswith("cal:"):
                    calibration_value = int(user_input[4:])
                    print(" Calibration mode active. Waiting for measurement...")
                elif user_input == "exit":
                    calibration_mode = False
                    print(" Calibration mode exited.")
                else:
                    print(" Invalid command. Use 'cal:<value>' to calibrate or 'exit' to exit calibration mode.")
        else:
            averageVoltage = medianVoltage * (VREF / 1024.0)
            compensationCoefficient = 1.0 + 0.02 * (temperature - 25.0)  # Temperature compensation
            compensationVoltage = averageVoltage / compensationCoefficient
            tdsValue = (133.42 * compensationVoltage**3 - 255.86 * compensationVoltage**2 + 857.39 * compensationVoltage) * 0.5
            print(" A1:%dppm " % tdsValue)

        if not calibration_mode:
            user_input = input(" Enter 'cal' to enter calibration mode, or press Enter to continue: ")
            if user_input == "cal":
                calibration_mode = True
                calibration_value = 0
                print(" Calibration mode activated. Enter calibration value (e.g., 707): ")
