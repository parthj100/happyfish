# 🐠 HappyFish Sensors & LED System

This project integrates pH, temperature, and TDS sensors with a Raspberry Pi, alongside a LED sunrise/sunset simulation system using a PCA9685 driver. Built during the **CUNY Spring Forward 2024** initiative, this system supports real-time monitoring and environmental simulation for aquatic ecosystems or smart farming.

---

## 📦 Features

- Live readings from pH, TDS, and temperature sensors
- LED sunrise and sunset lighting simulation
- Full integration via ADS1115 analog-to-digital converter
- Sensor calibration tools for accurate readings
- Scalable hardware setup for additional channels
- Environmentally aware LED dimming based on real-time clock
- Future-ready for web dashboard integration

---

## 🛠 Hardware Requirements

- Raspberry Pi (any model with GPIO + I2C)
- DS18B20 Temperature Sensor
- DFRobot pH Sensor
- TDS Sensor
- ADS1115 ADC module
- PCA9685 16-channel PWM LED driver
- 12–16 LEDs for simulation
- Jumper wires, breadboard, optional Adafruit Cobbler

---

## 🧰 Software Requirements

- Python 3
- `adafruit-circuitpython-pca9685`
- `DFRobot_PH.py`, `DFRobot_EC.py`, `CQRobot_ADS1115.py` (included in repo)
- Enable I2C and One-Wire via `sudo raspi-config`

---

## 📁 Key Python Files

### 🌡️ Sensor Scripts
- `temp.py`: Reads temperature from DS18B20 sensor
- `demo_PH_read.py`: Reads pH via ADS1115 and converts voltage
- `ADS1115_ReadVoltage.py`: Reads voltage from TDS sensor and computes ppm
- `demo_PH_calibration.py`: Calibrates pH sensor using buffer solutions
- `demo_PH_reset.py`: Resets pH calibration to defaults
- `demo_PH_EC.py`: Simultaneously reads temperature, EC, and pH

### 💡 LED Control
- `light_controller.py`: Simulates full-day cycle based on real-time system clock
- `sun_cycle_simulation.py`: Prompts user to simulate sunrise/sunset with LED dimming

### 🔄 Combined Scripts
- `happyfishV4.py`: Monitors temperature, pH, and TDS in real time
- `happyfishV5.py`: Includes all sensor readings plus LED lighting control with sunrise/sunset stages

---

## ⚙️ Setup Instructions

1. **Enable I2C and One-Wire:**
   ```bash
   sudo raspi-config

