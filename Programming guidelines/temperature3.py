import pigpio
import time

# Initialize pigpio
pi = pigpio.pi()

if not pi.connected:
    print("Failed to connect to pigpio daemon!")
    exit()

# Open SPI channel 0 (CE0), 1MHz speed, SPI mode 0
sensor = pi.spi_open(0, 1000000, 0)

def read_temperature(pi, sensor):
    c, d = pi.spi_read(sensor, 2)  # Read 2 bytes
    if c == 2:
        word = (d[0] << 8) | d[1]
        if (word & 0x4) == 0:  # Bit 2 should be 0 if no thermocouple error
            temp_c = (word >> 3) * 0.25
            return temp_c
        else:
            print("Thermocouple error detected!")
    else:
        print("SPI read error")
    return None

try:
    while True:
        temperature = read_temperature(pi, sensor)
        if temperature is not None:
            print(f"Temperature: {temperature:.2f} °C")
        time.sleep(1)

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    pi.spi_close(sensor)
    pi.stop()