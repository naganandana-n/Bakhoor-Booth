# fan testing - 19th may, 2025

import pigpio
import time

FAN_PIN = 21  # 18

pi = pigpio.pi()

if not pi.connected:
    print("Could not connect to pigpio daemon.")
    exit(1)

pi.set_mode(FAN_PIN, pigpio.OUTPUT)

try:
    while True:
        command = input("Type 'on' to turn fan ON, 'off' to turn it OFF, or 'exit' to quit: ").strip().lower()

        if command == 'on':
            pi.write(FAN_PIN, 1)
            print("Fan turned ON")
        elif command == 'off':
            pi.write(FAN_PIN, 0)
            print("Fan turned OFF")
        elif command == 'exit':
            break
        else:
            print("Invalid command. Type 'on', 'off', or 'exit'.")

except KeyboardInterrupt:
    print("\nExiting fan control...")

finally:
    pi.write(FAN_PIN, 0)  # Ensure fan is off
    pi.stop()