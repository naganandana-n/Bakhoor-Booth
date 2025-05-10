import pigpio
import time

pi = pigpio.pi()

# Define your custom SPI pins
CS_PIN = 21
CLK_PIN = 23
MISO_PIN = 24

# Initialize software SPI (bit-bang)
pi.bb_spi_open(CS_PIN, MISO_PIN, CLK_PIN, 1000000)  # CS, MISO, CLK, 1MHz

def read_temperature(pi):
    # Pull CS low to select the sensor
    pi.write(CS_PIN, 0)
    
    # Transfer 2 bytes (16 bits)
    count, data = pi.bb_spi_xfer(CS_PIN, [0x00, 0x00])
    
    # Pull CS high to end communication
    pi.write(CS_PIN, 1)

    if count == 2:
        word = (data[0] << 8) | data[1]
        if (word & 0x8006) == 0:
            t = (word >> 3) / 4.0
            return t
        else:
            print("Bad reading: {:b}".format(word))
    else:
        print("SPI read error")
    return None

try:
    while True:
        temp = read_temperature(pi)
        if temp is not None:
            print(f"Temperature: {temp:.2f} °C")
        time.sleep(1)

except KeyboardInterrupt:
    print("\nExiting...")
    pi.bb_spi_close(CS_PIN)
    pi.stop()