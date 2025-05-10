import pigpio
import time

pi = pigpio.pi()
sensor = pi.spi_open(0, 1000000, 0)  # SPI channel 0, 1MHz, mode 0

def read_temperature(pi, sensor):
    c, d = pi.spi_read(sensor, 2)
    if c == 2:
        word = (d[0] << 8) | d[1]
        if (word & 0x8006) == 0:
            t = (word >> 3) / 4.0
            return t
        else:
            print("Bad reading: {:b}".format(word))
    else:
        print("SPI read error")
    return None

while True:
    temp = read_temperature(pi, sensor)
    if temp:
        print(f"Temperature: {temp:.2f} °C")
    time.sleep(1)