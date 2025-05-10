import pigpio
import time

HEATER_PIN = 4  # your heater SSR pin
pi = pigpio.pi()

pi.set_mode(HEATER_PIN, pigpio.OUTPUT)

print("Heater ON")
pi.write(HEATER_PIN, 1)
time.sleep(5)

print("Heater OFF")
pi.write(HEATER_PIN, 0)
pi.stop()