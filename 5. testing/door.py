# door testing - 19th may, 2025

import pigpio

DOOR_PIN = 17 
pi = pigpio.pi()

if not pi.connected:
    print("Could not connect to pigpio daemon. Exiting.")
    exit(1)

pi.set_mode(DOOR_PIN, pigpio.OUTPUT)

print("Door Control Interface")
print("Type 'lock' to lock the door")
print("Type 'unlock' to unlock the door")
print("Type 'exit' to quit")

try:
    while True:
        command = input("Enter command (lock/unlock/exit): ").strip().lower()

        if command == "lock":
            pi.write(DOOR_PIN, 1)
            print("Door locked.")
        elif command == "unlock":
            pi.write(DOOR_PIN, 0)
            print("Door unlocked.")
        elif command == "exit":
            break
        else:
            print("Invalid command. Please type 'lock', 'unlock', or 'exit'.")
except KeyboardInterrupt:
    print("\nInterrupted by user.")

# Cleanup
pi.write(DOOR_PIN, 0)  # Unlock before exit, optional
pi.stop()
print("Exiting.")