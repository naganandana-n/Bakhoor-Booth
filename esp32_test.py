import serial
import time


ESP32_PORT = "/dev/ttyS0"   
BAUD_RATE = 9600

try:
    ser = serial.Serial(ESP32_PORT, BAUD_RATE, timeout=2)
    print(f"Connected to ESP32 on {ESP32_PORT}")
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    exit(1)

try:
    while True:
        ser.write(b'get_weight')  
        # ser.write(b'get_temp')
        response = ser.readline().decode().strip()

        if response.startswith("KG:"):
            weight = response.split(":")[1]
            print(f"Weight: {weight} kg")
        elif response.startswith("TEMP:"):
            temp = response.split(":")[1]
            print(f"Temperature: {temp} °C")
        else:
            print(f"Unexpected response: {response}")

        time.sleep(2)

except KeyboardInterrupt:
    print("\nExiting gracefully.")
    ser.close()