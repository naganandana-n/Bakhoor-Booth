# weight testing - 19th May, 2025

import serial
import time

ESP32_PORT = "/dev/ttyS0"  
BAUD_RATE = 9600

def get_weight():
    try:
        ser = serial.Serial(ESP32_PORT, BAUD_RATE, timeout=2)
        print(f"Connected to ESP32 on {ESP32_PORT}")
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return
    try:
        while True:
            ser.write(b'get_weight\n')
            response = ser.readline().decode().strip()
            if response.startswith("KG:"):
                weight = response.split(":")[1]
                print(f"Weight: {weight} kg")
            else:
                print(f"Unexpected response: {response}")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nExiting weight reading program.")
    finally:
        ser.close()

if __name__ == "__main__":
    get_weight()