import pigpio
import time

FAN_PIN = 18  

# Initialize pigpio
pi = pigpio.pi()
if not pi.connected:
    print("Failed to connect to pigpio daemon. Make sure 'sudo pigpiod' is running.")
    exit(1)

# Set pin mode
pi.set_mode(FAN_PIN, pigpio.OUTPUT)

try:
    print("\nFan PWM")
    print("Enter desired fan speed as percentage (0-100). Fan stays at last value until you change it.")
    print("Press Ctrl+C to exit.\n")

    current_pwm = 0
    pi.set_PWM_dutycycle(FAN_PIN, current_pwm)  # Start at 0%

    while True:
        user_input = input("Enter new PWM (%): ")

        try:
            pwm_percentage = float(user_input)
            if not 0 <= pwm_percentage <= 100:
                print("Please enter a value between 0 and 100.")
                continue

            # Convert percentage to duty cycle (0-255 for pigpio hardware PWM)
            duty_cycle = int(pwm_percentage * 255 / 100)
            pi.set_PWM_dutycycle(FAN_PIN, duty_cycle)
            current_pwm = pwm_percentage

            print(f"Fan PWM set to {current_pwm:.1f}%.")

        except ValueError:
            print("Invalid input. Please enter a number.")

except KeyboardInterrupt:
    print("\nExiting program...")

finally:
    pi.set_PWM_dutycycle(FAN_PIN, 0)  # Turn off fan
    pi.stop()
    print("Fan turned off.")