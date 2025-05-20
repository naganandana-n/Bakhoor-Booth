# heater testing - 19th may, 2025

import pigpio
import time

HEATER_PIN = 4 # 4
pi = pigpio.pi()

if not pi.connected:
    print("Could not connect to pigpio daemon.")
    exit(1)

pi.set_mode(HEATER_PIN, pigpio.OUTPUT)

try:
    while True:
        user_input = input("Enter heater ON time in seconds (or type 'exit' to quit): ").strip()
        if user_input.lower() == 'exit':
            break

        if not user_input.isdigit():
            print("Please enter a valid number.")
            continue

        duration = int(user_input)
        print(f"Heater ON for {duration} seconds")
        pi.write(HEATER_PIN, 1)
        time.sleep(duration)
        print("Heater OFF")
        pi.write(HEATER_PIN, 0)

except KeyboardInterrupt:
    print("\nExiting heater test...")

finally:
    pi.write(HEATER_PIN, 0)  # Make sure heater is off
    pi.stop()