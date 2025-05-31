#!/bin/bash

# Change to project directory
cd /home/pi/Desktop/Bakhoor-Booth

# Activate virtual environment
source venv/bin/activate

# Start pigpiod (only if not running)
if ! pgrep pigpiod > /dev/null; then
    sudo pigpiod
    sleep 1
fi

# Set display rotation (adjust HDMI-2 if needed)
xrandr --output HDMI-2 --rotate left

# Adjust touchscreen orientation
xinput set-prop "wch.cn USB2IIC_CTP_CONTROL" "Coordinate Transformation Matrix" 0 -1 1 1 0 0 0 0 1

# Run your main program
python 6.\ new_flow.py