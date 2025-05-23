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

### 4. Set Display Orientation
```bash
xrandr --output HDMI-1 --rotate left
xrandr --output HDMI-1 --rotate normal
```