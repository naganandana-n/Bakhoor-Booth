import pigpio
import time

DOOR_PIN = 17  # your door SSR pin
pi = pigpio.pi()

pi.set_mode(DOOR_PIN, pigpio.OUTPUT)

print("Door Lock ON")
pi.write(DOOR_PIN, 1)
time.sleep(5)

print("Door Lock OFF")
pi.write(DOOR_PIN, 0)
pi.stop()