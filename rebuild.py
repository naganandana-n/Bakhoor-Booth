import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
import atexit
from PIL import Image, ImageTk

# Raspberry Pi and Sensor Libraries
import pigpio
import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit
# from hx711 import HX711  # Uncomment when ready

class ThariBakhoorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Thari Bakhoor")
        self.geometry("600x1024")
        self.configure(bg="#f4e9e1")

        # Setup GPIO
        self.pi = pigpio.pi()
        GPIO.setmode(GPIO.BCM)
        if not self.pi.connected:
            self.destroy()

        # Setup pins
        self.heater_ssr_pin = 4
        self.door_ssr_pin = 17
        self.pi.set_mode(self.heater_ssr_pin, pigpio.OUTPUT)
        self.pi.set_mode(self.door_ssr_pin, pigpio.OUTPUT)

        # Fan setup
        self.kit = ServoKit(channels=16)
        self.fan_channels = list(range(16))
        self.initialize_fans_0()

        # Sensor placeholders
        self.sensor = self.pi.spi_open(0, 1000000, 0)  # For MAX6675
        # self.hx = HX711(dout_pin=18, pd_sck_pin=15)  # Uncomment and configure when ready

        # Threads and flags
        self.keep_running = True
        self.weight_check_thread = None
        self.person_running = False

        # Register cleanup
        atexit.register(self.cleanup_gpio)

        # Load splash
        self.splash_screen()

    # ----- UI Sections -----

    def splash_screen(self):
        try:
            image = Image.open("Assets/Splash.jpeg")  # Adjust path as needed
            tk_image = ImageTk.PhotoImage(image)
            self.logo_label = tk.Label(self, image=tk_image, bg="#f4e9e1")
            self.logo_label.image = tk_image
            self.logo_label.pack(expand=True)
        except Exception as e:
            print("Splash image not loaded:", e)
        self.after(3000, self.load_main_screen)

    def load_main_screen(self):
        if hasattr(self, 'logo_label'):
            self.logo_label.destroy()
        self.load_buttons()

    def load_buttons(self):
        self.button_frame = tk.Frame(self, bg="#f4e9e1")
        self.button_frame.pack(pady=20)

        ttk.Button(self.button_frame, text="Start System", command=self.start_system).pack(pady=10)
        ttk.Button(self.button_frame, text="Exit", command=self.destroy).pack()

    # ----- Function Placeholders -----

    def start_system(self):
        print("System starting...")
        # Add screen transitions, weight check, temp check, etc. step-by-step
        self.heater_on()

    def heater_on(self):
        self.pi.write(self.heater_ssr_pin, 1)
        print("Heater ON")

    def heater_off(self):
        self.pi.write(self.heater_ssr_pin, 0)
        print("Heater OFF")

    def initialize_fans_0(self):
        for channel in self.fan_channels:
            self.kit._pca.channels[channel].duty_cycle = 0

    def cleanup_gpio(self):
        print("Cleaning up GPIO...")
        self.heater_off()
        self.initialize_fans_0()
        GPIO.cleanup()
        self.pi.stop()

if __name__ == "__main__":
    app = ThariBakhoorApp()
    app.mainloop()