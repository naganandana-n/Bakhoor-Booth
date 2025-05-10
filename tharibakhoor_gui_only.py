
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from PIL import Image, ImageTk

ENABLE_HARDWARE = False  # Set to True when running on Raspberry Pi

class ThariBakhoorApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Thari Bakhoor")

        if ENABLE_HARDWARE:
            import pigpio
            import RPi.GPIO as GPIO
            from hx711 import HX711
            from adafruit_servokit import ServoKit
            import atexit

            self.pi = pigpio.pi()
            if not self.pi.connected:
                self.destroy()
            GPIO.setmode(GPIO.BCM)

            self.pi.set_mode(4, pigpio.OUTPUT)
            self.pi.set_mode(17, pigpio.OUTPUT)

            self.kit = ServoKit(channels=16)
            self.hx = HX711(dout_pin=18, pd_sck_pin=15)
            self.sensor = self.pi.spi_open(0, 1000000, 0)
            atexit.register(self.cleanup_gpio)
        else:
            self.pi = None
            self.kit = None
            self.hx = None
            self.sensor = None

        self.geometry("600x1024")
        self.configure(bg="#f4e9e1")
        self.custom_color = "#3e2d25"

        self.style = ttk.Style()
        self.style.theme_use('alt')
        self.style.configure("Custom.Veritcal.TProgressbar", background="#8B5742")

        self.splash_screen()

    def splash_screen(self):
        try:
            image = Image.open("/home/Arbitrary/Downloads/Assets/Splash.jpeg")
            tk_image = ImageTk.PhotoImage(image)
            self.logo_label = tk.Label(self, image=tk_image, bg="#f4e9e1")
            self.logo_label.image = tk_image
            self.logo_label.pack(expand=True)
        except:
            self.logo_label = tk.Label(self, text="Splash Screen", bg="#f4e9e1", font=("Arial", 24))
            self.logo_label.pack(expand=True)

        self.after(3000, self.load_main_screen)

    def load_main_screen(self):
        self.logo_label.destroy()
        self.load_logo()
        self.load_date_time()
        self.load_buttons()
        self.update_time()

    def load_logo(self):
        try:
            image1 = Image.open("/home/Arbitrary/Downloads/Assets/Logo.jpeg")
            logo_image = ImageTk.PhotoImage(image1)
            logo_label = tk.Label(self, image=logo_image, bg="#f4e9e1")
            logo_label.image = logo_image
            logo_label.pack(pady=20)
        except:
            logo_label = tk.Label(self, text="Thari Bakhoor", bg="#f4e9e1", font=("Arial", 24))
            logo_label.pack(pady=20)

    def load_date_time(self):
        self.time_label = tk.Label(self, font=("DM Sans", 16), bg="#f4e9e1")
        self.time_label.pack(pady=40)
        self.update_time()

    def update_time(self):
        current_time = datetime.now().strftime("%A, %d %B %Y \n %I:%M:%S %p")
        self.time_label.config(text=current_time)
        self.after(1000, self.update_time)

    def load_buttons(self):
        style = ttk.Style()
        style.configure("TButton", font=("DM Sans", 14))

        self.load_buttons_frame = tk.Frame(self, bg="#f4e9e1")
        self.load_buttons_frame.pack(pady=20)

        buttons = [("Person", self.dummy_screen), ("Clothes", self.dummy_screen),
                   ("Surrounding", self.dummy_screen), ("Custom", self.dummy_screen)]
        for idx, (text, cmd) in enumerate(buttons):
            row = idx // 3
            col = idx % 3
            button = ttk.Button(self.load_buttons_frame, text=text, command=cmd, width=10)
            button.grid(row=row, column=col, padx=10, pady=10)

    def dummy_screen(self):
        tk.messagebox.showinfo("Info", "GUI-only mode: Hardware functions disabled.")

    def cleanup_gpio(self):
        if self.pi:
            self.pi.write(4, 0)
            self.pi.write(17, 0)
            self.pi.stop()

if __name__ == "__main__":
    app = ThariBakhoorApp()
    app.mainloop()
