# Bakhoor-Booth

## Setup Instructions

### 1. Create and Activate a Virtual Environment
```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 2. Install Required Packages
```bash
pip install pillow pigpio RPi.GPIO adafruit-circuitpython-servokit
```

### 3. Start the pigpio Daemon
```bash
sudo pigpiod
```

### 4. Set Display Orientation (Potrait)
```bash
xrandr --output HDMI-1 --rotate left
xinput set-prop "wch.cn USB2IIC_CTP_CONTROL" "Coordinate Transformation Matrix" 0 -1 1 1 0 0 0 0 1
```

### 5. Reset Display Orientation (Landscape) - for Debugging
```bash
xrandr --output HDMI-1 --rotate normal
xinput set-prop "wch.cn USB2IIC_CTP_CONTROL" "Coordinate Transformation Matrix" 1 0 0 0 1 0 0 0 1
```