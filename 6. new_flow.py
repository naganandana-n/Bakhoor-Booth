import time
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from PIL import Image, ImageTk
import threading
import serial

ENABLE_HARDWARE = True  # Set to True when running on Raspberry Pi with full setup

if ENABLE_HARDWARE:
    import pigpio
    import RPi.GPIO as GPIO
    import atexit
    from adafruit_servokit import ServoKit


class ThariBakhoorApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Thari Bakhoor")
        if ENABLE_HARDWARE:
            self.pi = pigpio.pi()
            GPIO.setmode(GPIO.BCM)
        
            if not self.pi.connected:
                self.destroy()

            self.heater_ssr_pin = 5 #4
            self.door_ssr_pin = 17
            self.pi.set_mode(self.heater_ssr_pin, pigpio.OUTPUT)
            self.pi.set_mode(self.door_ssr_pin, pigpio.OUTPUT)
            self.fan_gpio_pin = 18
            GPIO.setup(self.fan_gpio_pin, GPIO.OUT)
            self.pi.set_mode(self.fan_gpio_pin, pigpio.OUTPUT)
            self.pi.write(self.fan_gpio_pin, 0)
            self.serial = serial.Serial("/dev/ttyS0", 9600, timeout=2)
            atexit.register(self.cleanup_gpio)
            # Lock the door by default for safety at startup
            self.pi.write(self.door_ssr_pin, 1)
        else:
            self.pi = None
            self.kit = None
            self.hx = None
            self.heater_ssr_pin = None
            self.door_ssr_pin = None
            self.fan_channels = []

        # self.geometry("600x1024")
        self.attributes("-fullscreen", True)

        self.bind("<Escape>", lambda e: self.destroy())

        self.configure(bg="#f4e9e1")  # Set background color for the entire application
         # Define the hexadecimal color code
        self.custom_color = "#3e2d25"  # Replace this with your desired color code
        # Initialize the style
        self.style = ttk.Style()
        self.style.theme_use('alt')
        # Configure the custom style
        self.style.configure("Custom.Vertical.TProgressbar", background="#8B5742")
        self.running = True
        self.person_running = False
        self.targettemp = [40, 120]
        # Splash screen
        self.splash_screen()

    def splash_screen(self):
        # Load the imageß
        try:
            image = Image.open("static/splash.png")

            # Convert the image to a Tkinter-compatible format
            tk_image = ImageTk.PhotoImage(image)

            # Create a Label widget to display the image
            self.logo_label = tk.Label(self, image=tk_image, bg="#f4e9e1")  # Store the logo label as an instance variable
            self.logo_label.image = tk_image  # Retain a reference to the image to prevent garbage collection
        except Exception as e:
            print(f"Warning: Splash image could not be loaded: {e}")
            self.logo_label = tk.Label(self, text="Thari Bakhoor", font=("Arial", 32), bg="#f4e9e1")
        self.logo_label.pack(expand=True)

        # "Touch to continue" label
        self.touch_label = tk.Label(self, text="Touch the screen to continue...", font=("DM Sans", 14), bg="#f4e9e1", fg="#555")
        self.touch_label.pack(pady=20)

        # Only run fan purge if hardware is enabled
        if ENABLE_HARDWARE:
            GPIO.output(self.fan_gpio_pin, GPIO.LOW)

        # Bind screen touch to continue
        self.bind("<Button-1>", self.on_splash_click)
        self.after(120000, self.on_splash_click, None)  # fallback auto-continue

    def on_splash_click(self, event):
        # Lock the door for safety at splash click (before main menu)
        if ENABLE_HARDWARE:
            self.pi.write(self.door_ssr_pin, 1)
        self.unbind("<Button-1>")
        self.logo_label.destroy()
        self.touch_label.destroy()
        self.load_main_screen()

    def load_main_screen(self):
        # Stops all the fans
        if ENABLE_HARDWARE:
            GPIO.output(self.fan_gpio_pin, GPIO.LOW)
            # Lock the door for safety at main menu
            self.pi.write(self.door_ssr_pin, 1)

        # Destroy splash screen widgets
        self.logo_label.destroy()

        # Load main screen widgets
        # Add main_frame as the parent for all main screen widgets
        self.main_frame = tk.Frame(self, bg="#f4e9e1")
        self.main_frame.pack(expand=True)

        # Load main screen widgets using main_frame as parent
        self.load_logo()
        self.load_date_time()
        self.load_buttons()
        # Always ensure the time is updating on the main screen
        self.update_time()

        
    def load_logo(self):
        try:
            image1 = Image.open("static/logo.png")
            image1 = image1.resize((300, 300), Image.Resampling.LANCZOS)  # Resize to fit the UI
            logo_image = ImageTk.PhotoImage(image1)
            logo_label = tk.Label(self.main_frame, image=logo_image, bg="#f4e9e1")
            logo_label.image = logo_image
        except Exception as e:
            print(f"Warning: Logo image not loaded: {e}")
            logo_label = tk.Label(self.main_frame, text="Thari Bakhoor", font=("Arial", 24, "bold"), bg="#f4e9e1")

        logo_label.pack(pady=20)

    def load_date_time(self):
        self.time_label = tk.Label(self.main_frame, font=("DM Sans", 16), bg="#f4e9e1")  # Set background color for the label
        self.time_label.pack(pady=40)
        self.update_time()

    def update_time(self):
        current_time = datetime.now().strftime("%A, %d %B %Y \n %I:%M:%S %p")
        if hasattr(self, "time_label") and self.time_label.winfo_exists():
            self.time_label.config(text=current_time)
        self.after(1000, self.update_time)

    def load_buttons(self):
        # Create a style object
        style = ttk.Style()

        # Configure the font for the buttons
        style.configure("TButton", font=("DM Sans", 14))
        self.load_buttons_frame = tk.Frame(self.main_frame, bg="#f4e9e1")  # Store the buttons frame as an instance variable
        self.load_buttons_frame.pack(pady=20)

        self.person_button = ttk.Button(self.load_buttons_frame, text="Person", command=self.show_person_screen, width=10, padding=5)
        self.person_button.grid(row=0, column=0, padx=10)

        self.clothes_button = ttk.Button(self.load_buttons_frame, text="Clothes", command=self.show_clothes_screen, width=10, padding=5)
        self.clothes_button.grid(row=0, column=1, padx=10)

        self.surrounding_button = ttk.Button(self.load_buttons_frame, text="Surrounding", command=self.show_surrounding_screen, width=10, padding=5)
        self.surrounding_button.grid(row=0, column=2, padx=10)

    def show_person_screen(self):
        # Destroy the buttons frame
        self.load_buttons_frame.destroy()
        self.running = False
        self.person_running = True

        self.center_frame = tk.Frame(self, bg="#f4e9e1")
        self.center_frame.pack(expand=True)

        self.heat_frame = tk.Frame(self.center_frame, bg="#f4e9e1")
        self.heat_frame.pack(pady=10)
        self.speed_frame = tk.Frame(self.center_frame, bg="#f4e9e1")
        self.speed_frame.pack(pady=10)
        self.time_frame = tk.Frame(self.center_frame, bg="#f4e9e1")
        self.time_frame.pack(pady=0)
        self.button_panel_frame = tk.Frame(self.center_frame, bg="#f4e9e1")
        self.button_panel_frame.pack(pady=0)
            
        # Heat Control Label
        heat_label = tk.Label(self.heat_frame, text="Heat Control", bg="#f4e9e1", font=("DM Sans", 12, "bold"))
        heat_label.grid(row=0, columnspan=3, pady=(0, 10))
        speed_label = tk.Label(self.speed_frame, text="Speed Control", bg="#f4e9e1", font=("DM Sans", 12, "bold"))
        speed_label.grid(row=0, columnspan=3, pady=(0, 10))
        time_label = tk.Label(self.time_frame, text="Time Control", bg="#f4e9e1", font=("DM Sans", 12, "bold"))
        
        time_label.grid(row=0, columnspan=3, pady=(0, 10))

        

        # HEAT CONTROL (3 bars: Low, Medium, High)
        self.heat_levels = [("Low", "110s+25s (2min)"), ("Medium", "120s+30s (2:10min)"), ("High", "130s+35s (2:20min)")]
        self.heat_buttons = []
        self.selected_heat_level = "Medium"  # Default selection
        for i, (level, label) in enumerate(self.heat_levels):
            btn = tk.Button(
                self.heat_frame,
                text=f"{level}\n{label}",
                font=("DM Sans", 12),
                width=10,
                relief="sunken" if level == self.selected_heat_level else "raised",
                command=lambda lvl=level: self.select_heat_level(lvl)
            )
            btn.grid(row=1, column=i, padx=10, pady=5)
            self.heat_buttons.append(btn)
        # Set initial heat parameters for default
        self.set_heat_params_from_level(self.selected_heat_level)

        # SPEED CONTROL (3 bars: 1, 2, 3)
        self.speed_levels = [("1", "150s"), ("2", "300s"), ("3", "480s")]
        self.speed_buttons = []
        self.selected_speed_value = 2  # Default selection is 2 (index=1)
        for i, (level, label) in enumerate(self.speed_levels):
            btn = tk.Button(
                self.speed_frame,
                text=f"{level}\n{label}",
                font=("DM Sans", 12),
                width=10,
                relief="sunken" if i == self.selected_speed_value - 1 else "raised",
                command=lambda idx=i: self.select_speed_level(idx)
            )
            btn.grid(row=1, column=i, padx=10, pady=5)
            self.speed_buttons.append(btn)

        # Set initial speed param
        self.set_speed_param_from_value(self.selected_speed_value)

        # TIME CONTROL (show total time as per heat+speed)
        # We'll update this label after both selections
        self.time_record = tk.Label(self.time_frame, text="", bg="#f4e9e1", font=("DM Sans", 12))
        self.time_record.grid(row=1, column=1, sticky="w")
        self.update_time_record_label()


        # Instructional message
        instruction_label = tk.Label(
            self.button_panel_frame,
            text="Ensure incense is placed in the chamber",
            font=("DM Sans", 12),
            bg="#f4e9e1",
            justify="center"
        )
        instruction_label.grid(row=0, column=0, columnspan=3, pady=(10, 5))

        # Create Save button to print values
        save_button = tk.Button(self.button_panel_frame, text="Start", command=self.save_values, font=("DM Sans", 12))
        save_button.grid(row=1, column=0, padx=(50, 10), pady=(10, 0)) # Place the Save button on the left

        # Safe Mode button
        safe_button = tk.Button(
            self.button_panel_frame,
            text="Safe Mode",
            command=self.activate_safe_mode,  # You can define this function
            font=("DM Sans", 12)
        )
        safe_button.grid(row=1, column=1, padx=10, pady=(10, 0))

        # Create Close button
        close_button = tk.Button(self.button_panel_frame, text="Close", command=self.show_main_screen_buttons, font=("DM Sans", 12))
        close_button.grid(row=1, column=2, padx=(10, 50), pady=(10, 0))  # Place the Close button on the right

    def select_heat_level(self, level):
        self.selected_heat_level = level
        for i, (lvl, _) in enumerate(self.heat_levels):
            self.heat_buttons[i].config(relief="sunken" if lvl == level else "raised")
        self.set_heat_params_from_level(level)
        self.update_time_record_label()

    def set_heat_params_from_level(self, level):
        # Map heat level to x_seconds, y_seconds, heat_duration
        if level == "Low":
            self.x_seconds = 110
            self.y_seconds = 25
            self.heat_duration = 120
        elif level == "Medium":
            self.x_seconds = 120
            self.y_seconds = 30
            self.heat_duration = 130
        elif level == "High":
            self.x_seconds = 130
            self.y_seconds = 35
            self.heat_duration = 140
        else:
            self.x_seconds = 120
            self.y_seconds = 30
            self.heat_duration = 130

    def select_speed_level(self, idx):
        self.selected_speed_value = idx + 1
        for i in range(len(self.speed_buttons)):
            self.speed_buttons[i].config(relief="sunken" if i == idx else "raised")
        self.set_speed_param_from_value(self.selected_speed_value)
        self.update_time_record_label()

    def set_speed_param_from_value(self, value):
        # value: 1, 2, 3
        if value == 1:
            self.speed_duration = 150
        elif value == 2:
            self.speed_duration = 300
        elif value == 3:
            self.speed_duration = 480
        else:
            self.speed_duration = 300

    def update_time_record_label(self):
        # Show a summary of the current settings (heat_duration + speed_duration)
        total_seconds = self.heat_duration + self.speed_duration
        mins = total_seconds // 60
        secs = total_seconds % 60
        self.time_record.config(text=f"Total: {mins}m {secs:02d}s")


    def show_clothes_screen(self):
        self.running = False
        # Destroy the buttons frame
        self.load_buttons_frame.destroy()

        # Centered frame for clothes mode
        self.center_frame = tk.Frame(self, bg="#f4e9e1")
        self.center_frame.pack(expand=True)

        self.heat_frame = tk.Frame(self.center_frame, bg="#f4e9e1")
        self.heat_frame.pack(pady=10)
        self.speed_frame = tk.Frame(self.center_frame, bg="#f4e9e1")
        self.speed_frame.pack(pady=10)
        self.time_frame = tk.Frame(self.center_frame, bg="#f4e9e1")
        self.time_frame.pack(pady=0)
        self.button_panel_frame = tk.Frame(self.center_frame, bg="#f4e9e1")
        self.button_panel_frame.pack(pady=0)

        # Section Headings
        heat_label = tk.Label(self.heat_frame, text="Heat Control", bg="#f4e9e1", font=("DM Sans", 12, "bold"))
        heat_label.grid(row=0, columnspan=3, pady=(0, 10))
        speed_label = tk.Label(self.speed_frame, text="Speed Control", bg="#f4e9e1", font=("DM Sans", 12, "bold"))
        speed_label.grid(row=0, columnspan=3, pady=(0, 10))
        time_label = tk.Label(self.time_frame, text="Time Control", bg="#f4e9e1", font=("DM Sans", 12, "bold"))
        time_label.grid(row=0, columnspan=3, pady=(0, 10))

        # HEAT CONTROL (3 bars: Low, Medium, High)
        self.clothes_heat_levels = [("Low", "110s+25s (2min)"), ("Medium", "120s+30s (2:10min)"), ("High", "130s+35s (2:20min)")]
        self.clothes_heat_buttons = []
        self.selected_clothes_heat_level = "Medium"  # Default selection
        for i, (level, label) in enumerate(self.clothes_heat_levels):
            btn = tk.Button(
                self.heat_frame,
                text=f"{level}\n{label}",
                font=("DM Sans", 12),
                width=10,
                relief="sunken" if level == self.selected_clothes_heat_level else "raised",
                command=lambda lvl=level: self.select_clothes_heat_level(lvl)
            )
            btn.grid(row=1, column=i, padx=10, pady=5)
            self.clothes_heat_buttons.append(btn)
        # Set initial heat parameters for default
        self.set_clothes_heat_params_from_level(self.selected_clothes_heat_level)

        # SPEED CONTROL (3 bars: 1, 2, 3)
        self.clothes_speed_levels = [("1", "150s"), ("2", "300s"), ("3", "480s")]
        self.clothes_speed_buttons = []
        self.selected_clothes_speed_value = 2  # Default selection is 2 (index=1)
        for i, (level, label) in enumerate(self.clothes_speed_levels):
            btn = tk.Button(
                self.speed_frame,
                text=f"{level}\n{label}",
                font=("DM Sans", 12),
                width=10,
                relief="sunken" if i == self.selected_clothes_speed_value - 1 else "raised",
                command=lambda idx=i: self.select_clothes_speed_level(idx)
            )
            btn.grid(row=1, column=i, padx=10, pady=5)
            self.clothes_speed_buttons.append(btn)

        # Set initial speed param
        self.set_clothes_speed_param_from_value(self.selected_clothes_speed_value)

        # TIME CONTROL (show total time as per heat+speed)
        self.clothes_time_record = tk.Label(self.time_frame, text="", bg="#f4e9e1", font=("DM Sans", 12))
        self.clothes_time_record.grid(row=1, column=1, sticky="w")
        self.update_clothes_time_record_label()

        # Instructional message
        instruction_label = tk.Label(
            self.button_panel_frame,
            text="Ensure incense is placed in the chamber",
            font=("DM Sans", 12),
            bg="#f4e9e1",
            justify="center"
        )
        instruction_label.grid(row=0, column=0, columnspan=3, pady=(10, 5))

        # Start button for clothes mode
        start_button = tk.Button(self.button_panel_frame, text="Start", command=self.start_clothes_mode_sequence, font=("DM Sans", 12))
        start_button.grid(row=1, column=0, padx=(50, 10), pady=(10, 0))

        # Safe Mode button - centered and styled to match other buttons
        safe_button = tk.Button(
            self.button_panel_frame,
            text="Safe Mode",
            command=self.activate_safe_mode,
            font=("DM Sans", 12),
            padx=10, pady=3
        )
        # Use grid to center the button in the column (column 1 of 3)
        safe_button.grid(row=1, column=1, padx=10, pady=(10, 0), sticky="nsew")
        self.button_panel_frame.grid_columnconfigure(0, weight=1)
        self.button_panel_frame.grid_columnconfigure(1, weight=1)
        self.button_panel_frame.grid_columnconfigure(2, weight=1)

        # Close button
        close_button = tk.Button(self.button_panel_frame, text="Close", command=self.show_main_screen_buttons, font=("DM Sans", 12))
        close_button.grid(row=1, column=2, padx=(10, 50), pady=(10, 0))

    def select_clothes_heat_level(self, level):
        self.selected_clothes_heat_level = level
        for i, (lvl, _) in enumerate(self.clothes_heat_levels):
            self.clothes_heat_buttons[i].config(relief="sunken" if lvl == level else "raised")
        self.set_clothes_heat_params_from_level(level)
        self.update_clothes_time_record_label()

    def set_clothes_heat_params_from_level(self, level):
        # Map heat level to x_seconds, y_seconds, heat_duration
        if level == "Low":
            self.clothes_x_seconds = 110
            self.clothes_y_seconds = 25
            self.clothes_heat_duration = 120
        elif level == "Medium":
            self.clothes_x_seconds = 120
            self.clothes_y_seconds = 30
            self.clothes_heat_duration = 130
        elif level == "High":
            self.clothes_x_seconds = 130
            self.clothes_y_seconds = 35
            self.clothes_heat_duration = 140
        else:
            self.clothes_x_seconds = 120
            self.clothes_y_seconds = 30
            self.clothes_heat_duration = 130

    def select_clothes_speed_level(self, idx):
        self.selected_clothes_speed_value = idx + 1
        for i in range(len(self.clothes_speed_buttons)):
            self.clothes_speed_buttons[i].config(relief="sunken" if i == idx else "raised")
        self.set_clothes_speed_param_from_value(self.selected_clothes_speed_value)
        self.update_clothes_time_record_label()

    def set_clothes_speed_param_from_value(self, value):
        # value: 1, 2, 3
        if value == 1:
            self.clothes_speed_duration = 150
        elif value == 2:
            self.clothes_speed_duration = 300
        elif value == 3:
            self.clothes_speed_duration = 480
        else:
            self.clothes_speed_duration = 300

    def update_clothes_time_record_label(self):
        total_seconds = getattr(self, "clothes_heat_duration", 130) + getattr(self, "clothes_speed_duration", 300)
        mins = total_seconds // 60
        secs = total_seconds % 60
        self.clothes_time_record.config(text=f"Total: {mins}m {secs:02d}s")

    def start_clothes_mode_sequence(self):
        # Stop any running threads to avoid interference
        self.running = False

        # Remove the heat, speed, time, and button_panel frames before starting clothes mode (like in Person Mode)
        self.time_frame.destroy()
        self.heat_frame.destroy()
        self.speed_frame.destroy()
        self.button_panel_frame.destroy()

        # Unlock the door at the start of the sequence so user can place clothes inside
        if ENABLE_HARDWARE:
            self.pi.write(self.door_ssr_pin, 0)

        # Assign heat and speed from current selections if available, else defaults
        self.clothes_heat_level = getattr(self, "selected_clothes_heat_level", "Medium")
        self.clothes_speed_value = getattr(self, "selected_clothes_speed_value", 2)

        # Set x_seconds and y_seconds based on clothes heat level
        if self.clothes_heat_level == "Low":
            self.clothes_x_seconds = 110
            self.clothes_y_seconds = 25
        elif self.clothes_heat_level == "Medium":
            self.clothes_x_seconds = 120
            self.clothes_y_seconds = 30
        elif self.clothes_heat_level == "High":
            self.clothes_x_seconds = 130
            self.clothes_y_seconds = 35
        else:
            self.clothes_x_seconds = 120
            self.clothes_y_seconds = 30

        # Set speed_duration based on selection
        if self.clothes_speed_value == 1:
            self.clothes_speed_duration = 150
        elif self.clothes_speed_value == 2:
            self.clothes_speed_duration = 300
        elif self.clothes_speed_value == 3:
            self.clothes_speed_duration = 480
        else:
            self.clothes_speed_duration = 300

        # Also update speed_end_time to match selected speed_duration
        self.clothes_speed_start_time = None  # will be set after weight=0
        self.clothes_speed_end_time = None

        # Show a new frame for the sequence
        self.clothes_mode_frame = tk.Frame(self, bg="#f4e9e1")
        self.clothes_mode_frame.pack(fill="both", expand=True)

        # Section label for process
        self.clothes_mode_label = tk.Label(self.clothes_mode_frame, text="Starting Clothes Mode...", font=("DM Sans", 16), bg="#f4e9e1")
        self.clothes_mode_label.pack(pady=40)

        # Centered Safe Mode button, styled to match other buttons
        safe_button = tk.Button(
            self.clothes_mode_frame,
            text="Safe Mode",
            command=self.activate_safe_mode,
            font=("DM Sans", 12),
            padx=10, pady=3
        )
        safe_button.pack(pady=10, anchor="center")

        # Start the controlled flow in a thread to avoid blocking the GUI
        threading.Thread(target=self._clothes_mode_flow, daemon=True).start()

    def _clothes_mode_flow(self):
        # Implements the new clothes mode logic with weight check and prompts.
        x = getattr(self, "clothes_x_seconds", 120)
        y = getattr(self, "clothes_y_seconds", 30)
        z = getattr(self, "clothes_speed_duration", 300)

        # 1. After clicking Start, check current weight
        weight = self._get_weight_value() if ENABLE_HARDWARE else 0
        if weight == 0:
            # Chamber is empty, lock the door and start heating cycle
            self._update_clothes_mode_label("Chamber empty. Locking door and starting cycle.")
            if ENABLE_HARDWARE:
                self.pi.write(self.door_ssr_pin, 1)
            time.sleep(2)
            # Proceed to heating cycle
        else:
            # Chamber not empty, unlock and prompt until weight is 0
            self._update_clothes_mode_label("Weight detected. Please remove any objects and close the door.")
            if ENABLE_HARDWARE:
                self.pi.write(self.door_ssr_pin, 0)
            time.sleep(2)
            # Wait for chamber to be empty
            self._update_clothes_mode_label("Waiting for chamber to be empty...")
            while True:
                weight = self._get_weight_value() if ENABLE_HARDWARE else 0
                if weight == 0:
                    break
                self._update_clothes_mode_label("Weight detected. Please remove any objects and close the door.")
                time.sleep(2)
            self._update_clothes_mode_label("Chamber empty. Locking door and starting cycle.")
            if ENABLE_HARDWARE:
                self.pi.write(self.door_ssr_pin, 1)
            time.sleep(2)

        # 2. Start Speed timer and begin heat cycle
        self.clothes_speed_start_time = time.time()
        self.clothes_speed_end_time = self.clothes_speed_start_time + z

        # Heater ON for X seconds (preheat)
        self._update_clothes_mode_label(f"Preheating... Heater ON for {x}s")
        if ENABLE_HARDWARE:
            self.heater_on(self.pi, self.heater_ssr_pin)
        preheat_start = time.time()
        while True:
            elapsed = int(time.time() - preheat_start)
            if elapsed >= x:
                break
            seconds_left = max(0, x - elapsed)
            self._update_clothes_mode_label(f"Preheating... Heater ON\n{seconds_left}s left")
            time.sleep(1)
        if ENABLE_HARDWARE:
            self.heater_off(self.pi, self.heater_ssr_pin)
        self._update_clothes_mode_label("Preheat done. Starting main heat cycle.")
        time.sleep(1)

        # After X seconds, turn on fan at 25% PWM
        if ENABLE_HARDWARE:
            self._set_fan_pwm(25)

        # 3. Alternate heater ON/OFF every Y seconds, check temp every 5s, for duration of Z (speed) timer
        last_temp_check = 0
        while time.time() < self.clothes_speed_end_time:
            now = time.time()
            # Check temp every 5s
            if now - last_temp_check >= 5:
                temp = self._get_temp_value()
                last_temp_check = now
                if temp >= 150:
                    self._update_clothes_mode_label(f"Temperature >150°C ({temp}°C).\nHeater OFF for {y}s.")
                    if ENABLE_HARDWARE:
                        self.heater_off(self.pi, self.heater_ssr_pin)
                    # Wait for Y seconds
                    for i in range(y):
                        if time.time() >= self.clothes_speed_end_time:
                            break
                        self._update_clothes_mode_label(f"Cooling (temp={temp}°C)... {y-i}s")
                        time.sleep(1)
                    continue
            # Heater ON for Y seconds
            self._update_clothes_mode_label(f"Heater ON for {y}s.")
            if ENABLE_HARDWARE:
                self.heater_on(self.pi, self.heater_ssr_pin)
            for i in range(y):
                if time.time() >= self.clothes_speed_end_time:
                    break
                z_remaining = max(0, int(self.clothes_speed_end_time - time.time()))
                y_remaining = max(0, y - i)
                self._update_clothes_mode_label(f"HEATER ON | Z: {z_remaining}s | Y: {y_remaining}s")
                # Check temp every 5s
                if (time.time() - last_temp_check) >= 5:
                    temp = self._get_temp_value()
                    last_temp_check = time.time()
                    if temp >= 150:
                        self._update_clothes_mode_label(f"Temperature >150°C ({temp}°C).\nHeater OFF for {y}s.")
                        if ENABLE_HARDWARE:
                            self.heater_off(self.pi, self.heater_ssr_pin)
                        break
                time.sleep(1)
            if time.time() >= self.clothes_speed_end_time:
                break
            # Heater OFF for Y seconds
            self._update_clothes_mode_label(f"Heater OFF for {y}s.")
            if ENABLE_HARDWARE:
                self.heater_off(self.pi, self.heater_ssr_pin)
            for i in range(y):
                if time.time() >= self.clothes_speed_end_time:
                    break
                z_remaining = max(0, int(self.clothes_speed_end_time - time.time()))
                y_remaining = max(0, y - i)
                self._update_clothes_mode_label(f"HEATER OFF | Z: {z_remaining}s | Y: {y_remaining}s")
                # Check temp every 5s
                if (time.time() - last_temp_check) >= 5:
                    temp = self._get_temp_value()
                    last_temp_check = time.time()
                    if temp >= 150:
                        self._update_clothes_mode_label(f"Temperature >150°C ({temp}°C).\nHeater OFF for {y}s.")
                        if ENABLE_HARDWARE:
                            self.heater_off(self.pi, self.heater_ssr_pin)
                        break
                time.sleep(1)
        # Ensure heater is OFF at the end
        if ENABLE_HARDWARE:
            self.heater_off(self.pi, self.heater_ssr_pin)
        self._update_clothes_mode_label("Heating cycle complete. Heater OFF.")
        time.sleep(1)

        # 4. At end of Speed timer, run fan at 100% for 3 min, then show 5-min cooldown
        self._update_clothes_mode_label("Post-cycle: Fan at 100% for 3 min.")
        if ENABLE_HARDWARE:
            self._set_fan_pwm(100)
        for i in range(180):
            self._update_clothes_mode_label(f"Fan 100%: {180-i}s left")
            time.sleep(1)
        if ENABLE_HARDWARE:
            self._set_fan_pwm(0)
        self._update_clothes_mode_label("Cooldown: 5 min safety timer.")
        # 5. Show 5-minute cooldown screen
        for i in range(5*60):
            mins = (5*60 - i) // 60
            secs = (5*60 - i) % 60
            self._update_clothes_mode_label(f"Please wait: {mins:02d}:{secs:02d} remaining (Cooldown)")
            # Also check temp every 5s, turn off heater if >150C
            if i % 5 == 0:
                temp = self._get_temp_value()
                if temp >= 150 and ENABLE_HARDWARE:
                    self.heater_off(self.pi, self.heater_ssr_pin)
            time.sleep(1)
        self._update_clothes_mode_label("Session complete. Unlocking door.")
        # Unlock door
        if ENABLE_HARDWARE:
            self.pi.write(self.door_ssr_pin, 0)
        time.sleep(2)
        self._update_clothes_mode_label("Done. Door unlocked.")
        time.sleep(3)
        self.clothes_mode_frame.after(0, self.show_main_screen_buttons)

    def _update_clothes_mode_label(self, message):
        if hasattr(self, "clothes_mode_label"):
            self.clothes_mode_label.config(
                text=message,
                font=("DM Sans", 12)
            )


    def show_surrounding_screen(self):
        self.running = False
        # Destroy the buttons frame
        self.load_buttons_frame.destroy()

        # Centered frame for surrounding mode
        self.center_frame = tk.Frame(self, bg="#f4e9e1")
        self.center_frame.pack(expand=True)

        self.heat_frame = tk.Frame(self.center_frame, bg="#f4e9e1")
        self.heat_frame.pack(pady=10)
        self.speed_frame = tk.Frame(self.center_frame, bg="#f4e9e1")
        self.speed_frame.pack(pady=10)
        self.time_frame = tk.Frame(self.center_frame, bg="#f4e9e1")
        self.time_frame.pack(pady=0)
        self.button_panel_frame = tk.Frame(self.center_frame, bg="#f4e9e1")
        self.button_panel_frame.pack(pady=0)

        # Heat Control Label
        heat_label = tk.Label(self.heat_frame, text="Heat Control", bg="#f4e9e1", font=("DM Sans", 12, "bold"))
        heat_label.grid(row=0, columnspan=3, pady=(0, 10))
        speed_label = tk.Label(self.speed_frame, text="Speed Control", bg="#f4e9e1", font=("DM Sans", 12, "bold"))
        speed_label.grid(row=0, columnspan=3, pady=(0, 10))
        time_label = tk.Label(self.time_frame, text="Time Control", bg="#f4e9e1", font=("DM Sans", 12, "bold"))
        time_label.grid(row=0, columnspan=3, pady=(0, 10))

        # HEAT CONTROL (3 bars: Low, Medium, High)
        self.surrounding_heat_levels = [("Low", "110s+25s (2min)"), ("Medium", "120s+30s (2:10min)"), ("High", "130s+35s (2:20min)")]
        self.surrounding_heat_buttons = []
        self.selected_surrounding_heat_level = "Medium"  # Default selection
        for i, (level, label) in enumerate(self.surrounding_heat_levels):
            btn = tk.Button(
                self.heat_frame,
                text=f"{level}\n{label}",
                font=("DM Sans", 12),
                width=10,
                relief="sunken" if level == self.selected_surrounding_heat_level else "raised",
                command=lambda lvl=level: self.select_surrounding_heat_level(lvl)
            )
            btn.grid(row=1, column=i, padx=10, pady=5)
            self.surrounding_heat_buttons.append(btn)
        # Set initial heat parameters for default
        self.set_surrounding_heat_params_from_level(self.selected_surrounding_heat_level)

        # SPEED CONTROL (3 bars: 1, 2, 3)
        self.surrounding_speed_levels = [("1", "150s"), ("2", "300s"), ("3", "480s")]
        self.surrounding_speed_buttons = []
        self.selected_surrounding_speed_value = 2  # Default selection is 2 (index=1)
        for i, (level, label) in enumerate(self.surrounding_speed_levels):
            btn = tk.Button(
                self.speed_frame,
                text=f"{level}\n{label}",
                font=("DM Sans", 12),
                width=10,
                relief="sunken" if i == self.selected_surrounding_speed_value - 1 else "raised",
                command=lambda idx=i: self.select_surrounding_speed_level(idx)
            )
            btn.grid(row=1, column=i, padx=10, pady=5)
            self.surrounding_speed_buttons.append(btn)

        # Set initial speed param
        self.set_surrounding_speed_param_from_value(self.selected_surrounding_speed_value)

        # TIME CONTROL (show total time as per heat+speed)
        # We'll update this label after both selections
        self.surrounding_time_record = tk.Label(self.time_frame, text="", bg="#f4e9e1", font=("DM Sans", 12))
        self.surrounding_time_record.grid(row=1, column=1, sticky="w")
        self.update_surrounding_time_record_label()

        # Instructional message
        instruction_label = tk.Label(
            self.button_panel_frame,
            text="Ensure incense is placed in the chamber",
            font=("DM Sans", 12),
            bg="#f4e9e1",
            justify="center"
        )
        instruction_label.grid(row=0, column=0, columnspan=3, pady=(10, 5))

        # Start button for surrounding mode
        save_button = tk.Button(self.button_panel_frame, text="Start", command=self.start_surrounding_mode_sequence, font=("DM Sans", 12))
        save_button.grid(row=1, column=0, padx=(50, 10), pady=(10, 0))

        # Safe Mode button
        safe_button = tk.Button(
            self.button_panel_frame,
            text="Safe Mode",
            command=self.activate_safe_mode,
            font=("DM Sans", 12)
        )
        safe_button.grid(row=1, column=1, padx=10, pady=(10, 0))

        # Close button
        close_button = tk.Button(self.button_panel_frame, text="Close", command=self.show_main_screen_buttons, font=("DM Sans", 12))
        close_button.grid(row=1, column=2, padx=(10, 50), pady=(10, 0))

    def select_surrounding_heat_level(self, level):
        self.selected_surrounding_heat_level = level
        for i, (lvl, _) in enumerate(self.surrounding_heat_levels):
            self.surrounding_heat_buttons[i].config(relief="sunken" if lvl == level else "raised")
        self.set_surrounding_heat_params_from_level(level)
        self.update_surrounding_time_record_label()

    def set_surrounding_heat_params_from_level(self, level):
        if level == "Low":
            self.surrounding_x_seconds = 110
            self.surrounding_y_seconds = 25
            self.surrounding_heat_duration = 120
        elif level == "Medium":
            self.surrounding_x_seconds = 120
            self.surrounding_y_seconds = 30
            self.surrounding_heat_duration = 130
        elif level == "High":
            self.surrounding_x_seconds = 130
            self.surrounding_y_seconds = 35
            self.surrounding_heat_duration = 140
        else:
            self.surrounding_x_seconds = 120
            self.surrounding_y_seconds = 30
            self.surrounding_heat_duration = 130

    def select_surrounding_speed_level(self, idx):
        self.selected_surrounding_speed_value = idx + 1
        for i in range(len(self.surrounding_speed_buttons)):
            self.surrounding_speed_buttons[i].config(relief="sunken" if i == idx else "raised")
        self.set_surrounding_speed_param_from_value(self.selected_surrounding_speed_value)
        self.update_surrounding_time_record_label()

    def set_surrounding_speed_param_from_value(self, value):
        if value == 1:
            self.surrounding_speed_duration = 150
        elif value == 2:
            self.surrounding_speed_duration = 300
        elif value == 3:
            self.surrounding_speed_duration = 480
        else:
            self.surrounding_speed_duration = 300

    def update_surrounding_time_record_label(self):
        total_seconds = getattr(self, "surrounding_heat_duration", 130) + getattr(self, "surrounding_speed_duration", 300)
        mins = total_seconds // 60
        secs = total_seconds % 60
        self.surrounding_time_record.config(text=f"Total: {mins}m {secs:02d}s")

    def start_surrounding_mode_sequence(self):
        # Stop any running threads to avoid interference
        self.running = False
        # Destroy the options page frames
        self.time_frame.destroy()
        self.heat_frame.destroy()
        self.speed_frame.destroy()
        self.button_panel_frame.destroy()
        # Lock the door
        if ENABLE_HARDWARE:
            self.pi.write(self.door_ssr_pin, 1)

        # Start speed timer immediately after door locks (before preheat X starts)
        self.surrounding_speed_start_time = time.time()
        self.surrounding_speed_end_time = self.surrounding_speed_start_time + getattr(self, "surrounding_speed_duration", 300)

        # Assign heat and speed from current selections
        self.surrounding_heat_level = getattr(self, "selected_surrounding_heat_level", "Medium")
        self.surrounding_speed_value = getattr(self, "selected_surrounding_speed_value", 2)

        # Set x_seconds and y_seconds based on surrounding heat level
        if self.surrounding_heat_level == "Low":
            self.surrounding_x_seconds = 110
            self.surrounding_y_seconds = 25
        elif self.surrounding_heat_level == "Medium":
            self.surrounding_x_seconds = 120
            self.surrounding_y_seconds = 30
        elif self.surrounding_heat_level == "High":
            self.surrounding_x_seconds = 130
            self.surrounding_y_seconds = 35
        else:
            self.surrounding_x_seconds = 120
            self.surrounding_y_seconds = 30

        # Set speed_duration based on selection
        if self.surrounding_speed_value == 1:
            self.surrounding_speed_duration = int(2.5 * 60)
        elif self.surrounding_speed_value == 2:
            self.surrounding_speed_duration = 5 * 60
        elif self.surrounding_speed_value == 3:
            self.surrounding_speed_duration = 8 * 60
        else:
            self.surrounding_speed_duration = 5 * 60

        # Also update speed_end_time to match selected speed_duration
        self.surrounding_speed_start_time = time.time()
        self.surrounding_speed_end_time = self.surrounding_speed_start_time + self.surrounding_speed_duration

        # Show a new frame for the sequence
        self.surrounding_mode_frame = tk.Frame(self, bg="#f4e9e1")
        self.surrounding_mode_frame.pack(fill="both", expand=True)
        self.surrounding_mode_label = tk.Label(self.surrounding_mode_frame, text="Starting Surrounding Mode...", font=("DM Sans", 16), bg="#f4e9e1")
        self.surrounding_mode_label.pack(pady=40)

        # Centered Safe Mode button, styled to match other buttons
        safe_button = tk.Button(
            self.surrounding_mode_frame,
            text="Safe Mode",
            command=self.activate_safe_mode,
            font=("DM Sans", 12),
            padx=10, pady=3
        )
        safe_button.pack(pady=10, anchor="center")

        # Start the controlled flow in a thread to avoid blocking the GUI
        threading.Thread(target=self._surrounding_mode_flow, daemon=True).start()

    def _surrounding_mode_flow(self):
        # Implements the new surrounding mode logic, using the same logic as clothes mode flow (without initial door unlock).
        x = getattr(self, "surrounding_x_seconds", 120)
        y = getattr(self, "surrounding_y_seconds", 30)
        z = getattr(self, "surrounding_speed_duration", 300)

        # Remove initial door unlock logic (as in clothes mode, but skip unlock at start)
        # Start Speed timer and begin heat cycle
        speed_start_time = time.time()
        speed_end_time = speed_start_time + z

        # Heater ON for X seconds (preheat)
        self._update_surrounding_mode_label(f"Preheating... Heater ON for {x}s")
        if ENABLE_HARDWARE:
            self.heater_on(self.pi, self.heater_ssr_pin)
        preheat_start = time.time()
        while True:
            elapsed = int(time.time() - preheat_start)
            if elapsed >= x:
                break
            seconds_left = max(0, x - elapsed)
            self._update_surrounding_mode_label(f"Preheating... Heater ON\n{seconds_left}s left")
            time.sleep(1)
        if ENABLE_HARDWARE:
            self.heater_off(self.pi, self.heater_ssr_pin)
        self._update_surrounding_mode_label("Preheat done. Starting main heat cycle.")
        time.sleep(1)

        # After X seconds, turn on fan at 25% PWM
        if ENABLE_HARDWARE:
            self._set_fan_pwm(25)

        # 3. Alternate heater ON/OFF every Y seconds, check temp every 5s, for duration of Z (speed) timer
        last_temp_check = 0
        while time.time() < speed_end_time:
            now = time.time()
            # Check temp every 5s
            if now - last_temp_check >= 5:
                temp = self._get_temp_value()
                last_temp_check = now
                if temp >= 150:
                    self._update_surrounding_mode_label(f"Temperature >150°C ({temp}°C).\nHeater OFF for {y}s.")
                    if ENABLE_HARDWARE:
                        self.heater_off(self.pi, self.heater_ssr_pin)
                    # Wait for Y seconds
                    for i in range(y):
                        if time.time() >= speed_end_time:
                            break
                        self._update_surrounding_mode_label(f"Cooling (temp={temp}°C)... {y-i}s")
                        time.sleep(1)
                    continue
            # Heater ON for Y seconds
            self._update_surrounding_mode_label(f"Heater ON for {y}s.")
            if ENABLE_HARDWARE:
                self.heater_on(self.pi, self.heater_ssr_pin)
            for i in range(y):
                if time.time() >= speed_end_time:
                    break
                z_remaining = max(0, int(speed_end_time - time.time()))
                y_remaining = max(0, y - i)
                self._update_surrounding_mode_label(f"HEATER ON | Z: {z_remaining}s | Y: {y_remaining}s")
                # Check temp every 5s
                if (time.time() - last_temp_check) >= 5:
                    temp = self._get_temp_value()
                    last_temp_check = time.time()
                    if temp >= 150:
                        self._update_surrounding_mode_label(f"Temperature >150°C ({temp}°C).\nHeater OFF for {y}s.")
                        if ENABLE_HARDWARE:
                            self.heater_off(self.pi, self.heater_ssr_pin)
                        break
                time.sleep(1)
            if time.time() >= speed_end_time:
                break
            # Heater OFF for Y seconds
            self._update_surrounding_mode_label(f"Heater OFF for {y}s.")
            if ENABLE_HARDWARE:
                self.heater_off(self.pi, self.heater_ssr_pin)
            for i in range(y):
                if time.time() >= speed_end_time:
                    break
                z_remaining = max(0, int(speed_end_time - time.time()))
                y_remaining = max(0, y - i)
                self._update_surrounding_mode_label(f"HEATER OFF | Z: {z_remaining}s | Y: {y_remaining}s")
                # Check temp every 5s
                if (time.time() - last_temp_check) >= 5:
                    temp = self._get_temp_value()
                    last_temp_check = time.time()
                    if temp >= 150:
                        self._update_surrounding_mode_label(f"Temperature >150°C ({temp}°C).\nHeater OFF for {y}s.")
                        if ENABLE_HARDWARE:
                            self.heater_off(self.pi, self.heater_ssr_pin)
                        break
                time.sleep(1)
        # Ensure heater is OFF at the end
        if ENABLE_HARDWARE:
            self.heater_off(self.pi, self.heater_ssr_pin)
        self._update_surrounding_mode_label("Heating cycle complete. Heater OFF.")
        time.sleep(1)

        # 4. At end of Speed timer, run fan at 100% for 3 min, then show 5-min cooldown
        self._update_surrounding_mode_label("Post-cycle: Fan at 100% for 3 min.")
        if ENABLE_HARDWARE:
            self._set_fan_pwm(100)
        for i in range(180):
            self._update_surrounding_mode_label(f"Fan 100%: {180-i}s left")
            time.sleep(1)
        if ENABLE_HARDWARE:
            self._set_fan_pwm(0)
        self._update_surrounding_mode_label("Cooldown: 5 min safety timer.")
        # 5. Show 5-minute cooldown screen
        for i in range(5*60):
            mins = (5*60 - i) // 60
            secs = (5*60 - i) % 60
            self._update_surrounding_mode_label(f"Please wait: {mins:02d}:{secs:02d} remaining (Cooldown)")
            # Also check temp every 5s, turn off heater if >150C
            if i % 5 == 0:
                temp = self._get_temp_value()
                if temp >= 150 and ENABLE_HARDWARE:
                    self.heater_off(self.pi, self.heater_ssr_pin)
            time.sleep(1)
        self._update_surrounding_mode_label("Session complete. Unlocking door.")
        # Unlock door
        if ENABLE_HARDWARE:
            self.pi.write(self.door_ssr_pin, 0)
        time.sleep(2)
        self._update_surrounding_mode_label("Done. Door unlocked.")
        time.sleep(3)
        self.surrounding_mode_frame.after(0, self.show_main_screen_buttons)

    def _update_surrounding_mode_label(self, message):
        if hasattr(self, "surrounding_mode_label"):
            self.surrounding_mode_label.config(text=message)
    def save_values(self):
        # Notes down the time at when the process starts
        self.saved_time = time.time()

        

        # Map heat level to x_seconds, y_seconds, heat_duration
        level = getattr(self, "selected_heat_level", "Medium")
        self.set_heat_params_from_level(level)
        speed_value = getattr(self, "selected_speed_value", 2)
        self.set_speed_param_from_value(speed_value)
        print(f"Heat Level: {self.selected_heat_level}, x_seconds={self.x_seconds}, y_seconds={self.y_seconds}, heat_duration={self.heat_duration}")
        print(f"Speed Value: {self.selected_speed_value}, speed_duration={self.speed_duration}")
        # Clean up frames

        self.time_frame.destroy()
        self.heat_frame.destroy()
        self.speed_frame.destroy()
        self.button_panel_frame.destroy()
        
        # Heating element is turned on.
        # Start the person mode sequence
        self.start_person_mode_sequence()

    def start_person_mode_sequence(self):
        # Stop any running threads to avoid interference
        self.running = False
        self.person_running = False 

        # Lock the door
        if ENABLE_HARDWARE:
            self.pi.write(self.door_ssr_pin, 1)

        # Start speed timer immediately after door locks (before preheat X starts)
        self.speed_start_time = time.time()
        self.speed_end_time = self.speed_start_time + getattr(self, "speed_duration", 300)

        # Before starting the mode flow, process heat level and speed to set x_seconds, y_seconds, speed_duration
        # Assign self.heat_level and self.speed_value from current selections
        self.heat_level = getattr(self, "selected_heat_level", "Medium")
        self.speed_value = getattr(self, "selected_speed_value", 2)

        # Set x_seconds and y_seconds based on self.heat_level
        if self.heat_level == "Low":
            self.x_seconds = 110
            self.y_seconds = 25
        elif self.heat_level == "Medium":
            self.x_seconds = 120
            self.y_seconds = 30
        elif self.heat_level == "High":
            self.x_seconds = 130
            self.y_seconds = 35
        else:
            self.x_seconds = 120
            self.y_seconds = 30  # Default

        # Set speed_duration based on self.speed_value
        if self.speed_value == 1:
            self.speed_duration = int(2.5 * 60)  # 2.5 minutes
        elif self.speed_value == 2:
            self.speed_duration = 5 * 60         # 5 minutes
        elif self.speed_value == 3:
            self.speed_duration = 8 * 60         # 8 minutes
        else:
            self.speed_duration = 5 * 60         # Default

        # Also update speed_end_time to match selected speed_duration
        self.speed_start_time = time.time()
        self.speed_end_time = self.speed_start_time + self.speed_duration

        # Show a new frame for the sequence
        self.person_mode_frame = tk.Frame(self, bg="#f4e9e1")
        self.person_mode_frame.pack(fill="both", expand=True)
        self.person_mode_label = tk.Label(self.person_mode_frame, text="Starting Person Mode...", font=("DM Sans", 16), bg="#f4e9e1")
        self.person_mode_label.pack(pady=40)

        # Centered Safe Mode button, styled to match clothes mode button
        safe_button = tk.Button(
            self.person_mode_frame,
            text="Safe Mode",
            command=self.activate_safe_mode,
            font=("DM Sans", 12),
            padx=10, pady=3
        )
        safe_button.pack(pady=10, anchor="center")

        # Start the controlled flow in a thread to avoid blocking the GUI
        threading.Thread(target=self._person_mode_flow, daemon=True).start()

    def _person_mode_flow(self):
        # Implements the full person mode flow, using self.speed_start_time and self.speed_end_time for Y-cycle.
        x = self.x_seconds
        y = self.y_seconds
        # Use speed timer from self.speed_start_time and self.speed_end_time
        # 1. Lock the door immediately
        if ENABLE_HARDWARE:
            self.pi.write(self.door_ssr_pin, 1)
        self._update_person_mode_label("Door locked.\nPreheating...")

        # 2. Turn on heater and start X timer (preheat)
        if ENABLE_HARDWARE:
            self.heater_on(self.pi, self.heater_ssr_pin)
        preheat_start = time.time()
        preheat_elapsed = 0
        entry_detected = False
        paused = False
        pause_start = None
        waited_while_zero = 0
        fan_10_after_unlock = False
        # 3. After 30s, unlock door for entry, but continue X timer (pause/resume if no entry)
        while preheat_elapsed < x:
            now = time.time()
            preheat_elapsed = int(now - preheat_start)
            seconds_left = max(0, x - preheat_elapsed)
            if preheat_elapsed < 30:
                self._update_person_mode_label(f"Preheating... {seconds_left}s left\nDoor unlocks in {30-preheat_elapsed}s")
                time.sleep(1)
                continue
            # Unlock the door at 30s if not already unlocked
            if preheat_elapsed == 30:
                self._update_person_mode_label("Unlocking door. Please enter chamber.")
                if ENABLE_HARDWARE:
                    self.pi.write(self.door_ssr_pin, 0)
                time.sleep(2)
                # After unlocking door, immediately turn fan ON at 10% PWM
                if ENABLE_HARDWARE:
                    self._set_fan_pwm(25)  # Fan at 10% after door unlocks
                fan_10_after_unlock = True
            # After 30s: check for entry
            weight = self._get_weight_value()
            # If no entry (weight == 0), pause X timer after 15s
            if not entry_detected:
                if weight == 0:
                    self._update_person_mode_label("Waiting for entry...\nPlease enter the chamber.")
                    waited_while_zero += 1
                    if waited_while_zero >= 15:
                        # Pause X timer, turn off heater, display message, wait for entry
                        paused = True
                        pause_start = time.time()
                        if ENABLE_HARDWARE:
                            self.heater_off(self.pi, self.heater_ssr_pin)
                        self._update_person_mode_label("Heater paused. Please enter chamber.")
                        while True:
                            weight = self._get_weight_value()
                            if weight > 50:
                                entry_detected = True
                                paused = False
                                if ENABLE_HARDWARE:
                                    self.heater_on(self.pi, self.heater_ssr_pin)
                                # Resume X timer from where left
                                pause_duration = int(time.time() - pause_start)
                                preheat_start += pause_duration
                                break
                            time.sleep(1)
                        continue
                    time.sleep(1)
                    continue
                elif 0 < weight <= 50:
                    # Not an adult
                    if ENABLE_HARDWARE:
                        self.heater_off(self.pi, self.heater_ssr_pin)
                    self._update_person_mode_label("Warning: not an adult.\nHeater OFF.")
                    time.sleep(5)
                    return
                elif weight > 50:
                    entry_detected = True
                    # Continue X timer, heater stays ON
                    self._update_person_mode_label(f"Entry detected.\nContinuing preheat: {seconds_left}s left.")
                    time.sleep(1)
                    continue
            # If already detected, just continue X timer
            self._update_person_mode_label(f"Preheating... ({seconds_left}s left)")
            time.sleep(1)
        # End of X timer: heater OFF
        if ENABLE_HARDWARE:
            self.heater_off(self.pi, self.heater_ssr_pin)
        self._update_person_mode_label("Preheat complete. Heater OFF.")
        time.sleep(1)

        # 4. Cyclic Y timer: alternate heater ON/OFF every Y seconds for speed_duration, with temperature checks
        # Use self.speed_start_time and self.speed_end_time as the timer.
        last_temp_check = 0
        # No further weight checks after person entry (per requirements)
        while time.time() < self.speed_end_time:
            now = time.time()
            # Check temp every 5s
            if now - last_temp_check >= 5:
                temp = self._get_temp_value()
                last_temp_check = now
                if temp >= 150:
                    self._update_person_mode_label(f"Temperature too high ({temp}°C). Heater OFF for {y}s.")
                    if ENABLE_HARDWARE:
                        self.heater_off(self.pi, self.heater_ssr_pin)
                    # Wait for Y seconds before continuing
                    for i in range(y):
                        if time.time() >= self.speed_end_time:
                            break
                        self._update_person_mode_label(f"Cooling (temp={temp}°C)... {y-i}s")
                        time.sleep(1)
                    continue
            # Heater OFF Y seconds
            self._update_person_mode_label(f"Heater OFF for {y}s.")
            if ENABLE_HARDWARE:
                self.heater_off(self.pi, self.heater_ssr_pin)
            for i in range(y):
                if time.time() >= self.speed_end_time:
                    break
                z_remaining = max(0, int(self.speed_end_time - time.time()))
                y_remaining = max(0, y - i)
                self._update_person_mode_label(f"HEATER OFF | remaining Z time: {z_remaining}s | Remaining Y time: {y_remaining}s")
                # Temperature safety
                if (time.time() - last_temp_check) >= 5:
                    temp = self._get_temp_value()
                    last_temp_check = time.time()
                    if temp >= 150:
                        self._update_person_mode_label(f"Temperature too high ({temp}°C). Heater OFF for {y}s.")
                        if ENABLE_HARDWARE:
                            self.heater_off(self.pi, self.heater_ssr_pin)
                        break
                time.sleep(1)
            if time.time() >= self.speed_end_time:
                break
            # Check temp before ON
            temp = self._get_temp_value()
            if temp >= 150:
                self._update_person_mode_label(f"Temperature still high ({temp}°C). Skipping ON cycle.")
                continue
            # Heater ON Y seconds
            self._update_person_mode_label(f"Heater ON for {y}s.")
            if ENABLE_HARDWARE:
                self.heater_on(self.pi, self.heater_ssr_pin)
            for i in range(y):
                if time.time() >= self.speed_end_time:
                    break
                z_remaining = max(0, int(self.speed_end_time - time.time()))
                y_remaining = max(0, y - i)
                self._update_person_mode_label(f"HEATER ON | remaining Z time: {z_remaining}s | Remaining Y time: {y_remaining}s")
                if (time.time() - last_temp_check) >= 5:
                    temp = self._get_temp_value()
                    last_temp_check = time.time()
                    if temp >= 150:
                        self._update_person_mode_label(f"Temperature too high ({temp}°C). Heater OFF for {y}s.")
                        if ENABLE_HARDWARE:
                            self.heater_off(self.pi, self.heater_ssr_pin)
                        break
                time.sleep(1)
        # Ensure heater is OFF at the end
        if ENABLE_HARDWARE:
            self.heater_off(self.pi, self.heater_ssr_pin)
        self._update_person_mode_label("Heating cycle complete. Heater OFF.")
        time.sleep(1)

        # 5. FAN CONTROL: After speed timer ends, run fan at 10% PWM for 30s, then 100% PWM for 3 min
        self._update_person_mode_label("Cooling: Fan 10% for 30s...")
        if ENABLE_HARDWARE:
            self._set_fan_pwm(25)
        for i in range(30):
            self._update_person_mode_label(f"Cooling: Fan 10% for {30-i}s")
            time.sleep(1)
        self._update_person_mode_label("Cooling: Fan 100% for 3 min...")
        if ENABLE_HARDWARE:
            self._set_fan_pwm(100)
        for i in range(180):
            self._update_person_mode_label(f"Cooling: Fan 100% for {180-i}s")
            time.sleep(1)
        if ENABLE_HARDWARE:
            self._set_fan_pwm(0)
        self._update_person_mode_label("Cooling complete. Fan OFF.")
        time.sleep(1)

        # 6. Show 5-minute timer display (user can see countdown)
        self._update_person_mode_label("Please wait: 5 min timer for safety.")
        for i in range(5*60):
            mins = (5*60 - i) // 60
            secs = (5*60 - i) % 60
            self._update_person_mode_label(f"Please wait: {mins:02d}:{secs:02d} remaining")
            # Also check temp every 5s, turn off heater if >150C
            if i % 5 == 0:
                temp = self._get_temp_value()
                if temp >= 150 and ENABLE_HARDWARE:
                    self.heater_off(self.pi, self.heater_ssr_pin)
            time.sleep(1)
        self._update_person_mode_label("Session complete. Unlocking door.")
        # 7. Unlock door
        if ENABLE_HARDWARE:
            self.pi.write(self.door_ssr_pin, 0)
        time.sleep(2)
        self._update_person_mode_label("Done. Door unlocked.")
        time.sleep(3)
        self.person_mode_frame.after(0, self.show_main_screen_buttons)

    def _set_fan_pwm(self, percent):
        # Helper to set fan GPIO PWM (software fallback if no hardware PWM)
        if not ENABLE_HARDWARE:
            print(f"[SIMULATED] Fan set to {percent}% PWM")
            return
        # Use pigpio hardware PWM if available
        try:
            # pigpio.set_PWM_dutycycle(gpio, dutycycle) where dutycycle is 0-255
            duty = int(percent * 255 / 100)
            self.pi.set_PWM_dutycycle(self.fan_gpio_pin, duty)
        except Exception as e:
            print(f"Error setting fan PWM: {e}")
    
    # Acts as a preheating screen, displays data while heating element reaches targettemp[1]
    def waiting_screen(self):
        # Heating element relay turned on
        # Time note when heating element is turned on
        self.wait_frame = tk.Frame(self, bg="#f4e9e1")
        self.wait_frame.pack(pady=0)
        self.main_label = tk.Label(self.wait_frame, text="Please wait, \nSystem heating up", bg="#f4e9e1", font=("DM Sans", 18, "bold"))
        self.main_label.grid(row=1, columnspan=5, pady=(0, 10))

        if ENABLE_HARDWARE:
            # Convert target temperature to integer
            target_temp = int(self.targettemp[1])

            # Update the waiting label after 2 seconds
            self.after(2000, lambda: self.start_temperature_check(target_temp))
        else:
            # Simulate wait and skip temperature check
            self.after(2000, self.update_waiting_label)

    def start_temperature_check(self, target_temp):
        if ENABLE_HARDWARE:
            actual_heat_value = self.check_heat_value()
            print(actual_heat_value)

            while True:
                temperature = self.read_temperature(self.pi, target_temp)
                if temperature >= 450:
                    print(" EMERGENCY: Heater turned OFF due to temperature > 450°C during preheat")
                    self.heater_off(self.pi, self.heater_ssr_pin)
                    messagebox.showerror("Overheat Alert", "Temperature exceeded 450°C! Heater has been shut down.")
                    return  # Exit without proceeding

                if temperature > target_temp:
                    break
                time.sleep(1)

            self.update_waiting_label()
        else:
            print("[SIMULATION] Skipping temperature check (GUI-only mode)")
            self.update_waiting_label()

    def update_waiting_label(self):
        # Updates the label when the temperature in the preheating screen is met
        self.main_label.config(text = "PLEASE STEP INSIDE")
        self.after(3000, self.working_screen)

    def working_screen(self):
        # Print pre-defined temperature
        print("Pre-defined temp is:", self.assigned_heat)
        print("Pre-defined speed: ", self.assigned_speed)
        # Starts the fans as per the value assigned to them in their respective screen (Human, Clothes, Surrounding)
        if ENABLE_HARDWARE:
            # channel_duty_cycle = self.check_speed_value()
            # self.control_fans(self.kit, self.fan_channels, channel_duty_cycle)
            GPIO.output(self.fan_gpio_pin, GPIO.HIGH)

        # Calculate min and max heat values
        min_heat = self.assigned_heat - 20
        max_heat = self.assigned_heat + 5
        heater_on = False

        # Updates the time_remaining for the session.
        def update_remaining_time(time_remaining_label):

            nonlocal heater_on 
            
            def format_time(minutes, seconds):
                return "{} minutes {} seconds".format(int(minutes), int(seconds))

            current_time = time.time()
            elapsed_time = current_time - self.saved_time

            time_value_seconds = int(self.assigned_time * 60)

            remaining_time = max(0, time_value_seconds - elapsed_time)
            remaining_minutes = remaining_time // 60
            remaining_seconds = remaining_time % 60

            formatted_time = format_time(remaining_minutes, remaining_seconds)

            time_remaining_label.config(text="Time Remaining:\n {}".format(formatted_time))
            
            if remaining_time == 0:
                self.cooling_down_screen()
            else:
                # Check temperature only if time remaining is not 0
                if ENABLE_HARDWARE:
                    temperature = self.read_temperature(self.pi, self.targettemp[1])
                    if temperature is not None:
                        if temperature >= 450:
                            print(" EMERGENCY: Temperature exceeded 450°C. Shutting down heater.")
                            self.heater_off(self.pi, self.heater_ssr_pin)
                            messagebox.showerror("Overheat Alert", "Temperature exceeded 450°C! Heater has been shut down.")
                            self.cooling_down_screen()
                            return  # Immediately exit to prevent further execution
                        
                        if min_heat <= temperature <= max_heat and heater_on:
                            self.heater_off(self.pi, self.heater_ssr_pin)
                            heater_on = False
                        elif temperature > max_heat and heater_on:
                            self.heater_off(self.pi, self.heater_ssr_pin)
                            heater_on = False
                        elif temperature < min_heat and not heater_on:
                            self.heater_on(self.pi, self.heater_ssr_pin)
                            heater_on = True

                time_remaining_label.after(1000, update_remaining_time, time_remaining_label)

        self.wait_frame.destroy()
        self.working_frame = tk.Frame(self, bg="#f4e9e1")
        self.working_frame.pack(pady=0)
        self.time_remaining_label = tk.Label(self.working_frame, text="", bg="#f4e9e1", font=("DM Sans", 20, "bold"))
        self.time_remaining_label.grid(row=1, columnspan=5, pady=(0, 10))

        update_remaining_time(self.time_remaining_label)    

    # The cooling down screen is used stop the fans, heaters and stop the user to use the system again before cooling down
    # targettemp[0] is used for the cooling down temp limit 
    def cooling_down_screen(self):
        if ENABLE_HARDWARE:
            self.heater_off(self.pi, self.heater_ssr_pin)
            # self.initialize_fans_0(self.kit, self.fan_channels)
            GPIO.output(self.fan_gpio_pin, GPIO.LOW)
        self.reset_assigned_value()
        if ENABLE_HARDWARE:
            # self.cooling_system_down()
            GPIO.output(self.fan_gpio_pin, GPIO.HIGH)
        self.working_frame.destroy()
        self.cooling_down_frame = tk.Frame(self, bg="#f4e9e1")
        self.cooling_down_frame.pack(pady=0)
        self.cool_label = tk.Label(self.cooling_down_frame, text="Cooling Down", bg="#f4e9e1", font=("DM Sans", 12, "bold"))
        self.cool_label.grid(row=1, columnspan = 5 , pady=(0,10))
        
    # Define a function to continuously check temperature
        def check_temperature():
            if ENABLE_HARDWARE:
                temperature = self.read_temperature(self.pi, self.targettemp[0])
                if temperature is not None and temperature < self.targettemp[0]:
                    for widget in self.winfo_children():
                        widget.destroy()
                    # self.initialize_fans_0(self.kit, self.fan_channels)
                    GPIO.output(self.fan_gpio_pin, GPIO.LOW)
                    self.running = True
                    self.person_running = False
                    self.load_main_screen()
                else:
                    self.after(1000, check_temperature)
            else:
                def simulate_reset():
                    for widget in self.winfo_children():
                        widget.destroy()
                    self.running = True
                    self.person_running = False
                    self.load_main_screen()

                self.after(3000, simulate_reset)

        # Start checking temperature
        check_temperature()

    def reset_assigned_value(self):
        self.assigned_heat = 3
        self.assigned_speed = 3
        self.assigned_time = 2
        self._saved_time = 0.0 # self.saved_time
        
    def show_custom_screen(self):
        self.running = False
        self.person_running = True

        # Destroy the buttons frame
        self.load_buttons_frame.destroy()

        # Load frames for Heat, Speed, and Time
        self.heat_frame = tk.Frame(self, bg="#f4e9e1")
        self.heat_frame.pack(pady=10)
        self.speed_frame = tk.Frame(self, bg="#f4e9e1")
        self.speed_frame.pack(pady=10)
        self.time_frame = tk.Frame(self, bg="#f4e9e1")
        self.time_frame.pack(pady=0)
        self.button_panel_frame = tk.Frame(self, bg="#f4e9e1")
        self.button_panel_frame.pack(pady=0)

        # Heat Control Label
        heat_label = tk.Label(self.heat_frame, text="Heat Control", bg="#f4e9e1", font=("DM Sans", 12, "bold"))
        heat_label.grid(row=4, columnspan=5, pady=(0, 10))
        speed_label = tk.Label(self.speed_frame, text="Speed Control", bg="#f4e9e1", font=("DM Sans", 12, "bold"))
        speed_label.grid(row=4, columnspan=5, pady=(0, 10))
        time_label = tk.Label(self.time_frame, text="Time Control", bg="#f4e9e1", font=("DM Sans", 12, "bold"))
        time_label.grid(row=4, columnspan=5, pady=(0, 10))

        # Lengths for each progress bar
        bar_lengths = [20, 40, 60, 80, 100]

        # Create and pack 5 progress bars in heat_frame
        self.heat_progress_bars = []
        for i, length in enumerate(bar_lengths):
            progress_bar = ttk.Progressbar(self.heat_frame, orient=tk.VERTICAL, length=length, mode='determinate', style="Custom.Vertical.TProgressbar")
            progress_bar.grid(row=1, column=i, padx=5, sticky="s")  # Align bottom using "s"
            self.heat_progress_bars.append(progress_bar)

        # Create and pack 5 progress bars in speed_frame
        self.speed_progress_bars = []
        for i, length in enumerate(bar_lengths):
            progress_bar = ttk.Progressbar(self.speed_frame, orient=tk.VERTICAL, length=length, mode='determinate', style="Custom.Vertical.TProgressbar")
            progress_bar.grid(row=1, column=i, padx=5, sticky="s")  # Align bottom using "s"
            self.speed_progress_bars.append(progress_bar)

        # Set the background color for all progress bars
        self.style.configure("Custom.Vertical.TProgressbar", background="#8B5742")

        # Bind left mouse button click event to fill_progress function for heat progress bars
        for progress_bar in self.heat_progress_bars:
            progress_bar.bind("<Button-1>", lambda event, pb=progress_bar: self.fill_progress(event, pb))
            # Bind finger touch event to fill_progress function
            progress_bar.bind("<ButtonPress-1>", lambda event, pb=progress_bar: self.fill_progress(event, pb))

        # Bind left mouse button click event to fill_progress function for speed progress bars
        for progress_bar in self.speed_progress_bars:
            progress_bar.bind("<Button-1>", lambda event, pb=progress_bar: self.fill_progress(event, pb))
            # Bind finger touch event to fill_progress function
            progress_bar.bind("<ButtonPress-1>", lambda event, pb=progress_bar: self.fill_progress(event, pb))

        # Create a time label and control it
        time_heading = tk.Label(self.time_frame, text="Time: ", bg="#f4e9e1", font=("DM Sans", 12))
        time_heading.grid(row=1, column=1, sticky="e")
        self.time_record = tk.Label(self.time_frame, text="00:00:00", bg="#f4e9e1", font=("DM Sans", 12))
        self.time_record.grid(row=1, column=2, sticky="w")

        # Create buttons with custom appearance and functionality
        time_clear = tk.Button(self.time_frame, text="Clear", command=self.clear_time, font=("DM Sans", 12), width=10)
        time_clear.grid(row=2, column=0, padx=10, pady=5)

        time_1_ = tk.Button(self.time_frame, text="+1", command=lambda: self.add_time(1), font=("DM Sans", 12), width=8)
        time_1_.grid(row=2, column=1, padx=10, pady=5)

        time_5_ = tk.Button(self.time_frame, text="+5", command=lambda: self.add_time(5), font=("DM Sans", 12), width=8)
        time_5_.grid(row=2, column=2, padx=10, pady=5)

        time_10_ = tk.Button(self.time_frame, text="+10", command=lambda: self.add_time(10), font=("DM Sans", 12), width=8)
        time_10_.grid(row=2, column=3, padx=10, pady=5)

        # Instruction Label
        self.instruction_label = tk.Label(
            self.button_panel_frame,
            text="",
            bg="#f4e9e1",
            font=("DM Sans", 12)
        )
        self.instruction_label.grid(row=0, column=1, pady=(10, 0))

        # Create Save button to print values
        save_button = tk.Button(self.button_panel_frame, text="Start", command=self.save_values if ENABLE_HARDWARE else self.custom_save_values, font=("DM Sans", 12))
        save_button.grid(row=1, column=0, padx=(50, 10), pady=(10, 0))  # Place the Save button on the left

        # Safe Mode button
        safe_button = tk.Button(
            self.button_panel_frame,
            text="Safe Mode",
            command=self.activate_safe_mode,  # You can define this function
            font=("DM Sans", 12)
        )
        safe_button.grid(row=1, column=1, padx=10, pady=(10, 0))

        # Create Close button
        close_button = tk.Button(self.button_panel_frame, text="Close", command=self.show_main_screen_buttons, font=("DM Sans", 12))
        close_button.grid(row=1, column=2, padx=(10, 50), pady=(10, 0))  # Place the Close button on the right


    def custom_save_values(self):
        # Store current selections for simulation
        heat_value = sum(1 for pb in self.heat_progress_bars if pb["value"] == 100)
        speed_value = sum(1 for pb in self.speed_progress_bars if pb["value"] == 100)
        time_value = self.get_time_value()

        print("Heat value (GUI only):", heat_value)
        print("Speed value (GUI only):", speed_value)
        print("Time value (GUI only):", time_value)

        # Store the values like in normal mode
        self.assigned_heat = heat_value
        self.assigned_speed = speed_value
        self.assigned_time = time_value
        self.saved_time = time.time()

        # Clean up frames
        self.time_frame.destroy()
        self.heat_frame.destroy()
        self.speed_frame.destroy()
        self.button_panel_frame.destroy()

        # Simulate heater wait + transition to working screen
        self.waiting_screen()



    def get_time_value(self):
        try:
            current_time = self.time_record["text"]
            hours, minutes, seconds = map(int, current_time.split(":"))
            total_minutes = hours * 60 + minutes + (seconds / 60)
            return total_minutes
        except ValueError:
            return 0
        
    

    def show_main_screen_buttons(self):
        # Destroy the custom screen
        for widget in self.winfo_children():
            widget.destroy()

        # Add main_frame as the parent for all main screen widgets
        self.main_frame = tk.Frame(self, bg="#f4e9e1")
        self.main_frame.pack(expand=True)


        # Reload the main screen buttons
        self.load_logo()
        self.load_date_time()
        self.load_buttons()
    
        self.running = True
        self.person_running = False

        

    def cleanup_gpio(self):
        if ENABLE_HARDWARE:
            # Turn off all heaters
            self.heater_off(self.pi, self.heater_ssr_pin)
            # Turn off all fans
            # self.initialize_fans_0(self.kit, self.fan_channels)
            GPIO.output(self.fan_gpio_pin, GPIO.LOW)
            # Close GPIO pins
            GPIO.cleanup()
            # Disconnect from pigpio
            self.pi.stop()

    # Override the default destroy method of your Tkinter application
    def destroy(self):
        # Call the cleanup method before destroying the application
        self.cleanup_gpio()
        # Call the destroy method of the super class
        super().destroy()    

    def clear_time(self):
        self.time_record.config(text="00:00:00")

    def add_time(self, minutes):
        current_time = self.time_record["text"]
        total_hours = 0  # Initialize total_hours
        try:
            current_hours, current_minutes, current_seconds = map(int, current_time.split(":"))
            total_minutes = current_minutes + minutes
            total_seconds = current_seconds

            # Ensure total time does not exceed 90 minutes (1 hour 30 minutes)
            if current_hours == 1 and current_minutes >= 30:
                messagebox.showinfo("Limit Reached", "Maximum time limit reached (1 hour 30 minutes)")
                return  # Stop further execution

            # Handle incrementing hours if total minutes exceed 60
            if total_minutes >= 60:
                total_hours = current_hours + 1  # Increment hour by 1
                total_minutes -= 60              # Subtract 60 to keep the minutes within 0-59 range

            else:
                total_hours = current_hours  # No change in hours

            # Ensure total time does not exceed 90 minutes (1 hour 30 minutes)
            if total_hours == 1 and total_minutes > 30:
                total_minutes = 30
                messagebox.showinfo("Limit Reached", "Maximum time limit reached (1 hour 30 minutes)")

            self.time_record.config(text="{:02d}:{:02d}:{:02d}".format(total_hours, total_minutes, total_seconds))
        except ValueError:
            messagebox.showerror("Error", "Invalid time format")

    def fill_progress(self, event, clicked_progress_bar):
        # Determine the index of the clicked progress bar
        if clicked_progress_bar in self.heat_progress_bars:
            progress_bars = self.heat_progress_bars
            print("Clicked progress bar is in heat_progress_bars")
        elif clicked_progress_bar in self.speed_progress_bars:
            progress_bars = self.speed_progress_bars
            print("Clicked progress bar is in speed_progress_bars")

        clicked_index = progress_bars.index(clicked_progress_bar)

        # Print the values of the progress bars
        print("Progress bar values before update:", [pb["value"] for pb in progress_bars])

        # Apply the style to the clicked progress bar
        clicked_progress_bar["style"] = "Custom.Vertical.TProgressbar"

        # Iterate through all progress bars
        for i, progress_bar in enumerate(progress_bars):
            # If the current progress bar is before or at the clicked index,
            # set its value to 100 and change its color, otherwise set it to 0
            progress_bar["value"] = 100 if i <= clicked_index else 0

        # Print the updated values of the progress bars
        print("Progress bar values after update:", [pb["value"] for pb in progress_bars])



#Code for the python-sensorsdef check_person_weight(self):
    def check_person_weight(self): 
        if ENABLE_HARDWARE:
            weight_safe = self.checking_weight()
            if weight_safe:
                print("Weight detected, auto start happening as more than 50kg")
                self.auto_start_save()
            else:
                print("Weight not detected, auto start will not be activated")
        else:
            print("[GUI-only] Skipping weight check.")

    

    def initialize_weight(self):
        print("Weight initialization handled by ESP32 via serial.")
        

    def checking_weight(self):
        if not ENABLE_HARDWARE:
            print("[GUI-only] Skipping weight check. Returning False.")
            return False
        try:
            self.serial.write(b'get_weight\n')
            response = self.serial.readline().decode().strip()
            if response.startswith("KG:"):
                weight_kg = float(response.split(":")[1])
                print(f"Weight: {weight_kg:.2f} kg")
                return weight_kg > 4.00
            else:
                print(f"Unexpected weight response: {response}")
                return False
            
        except Exception as e:
            print(f"Serial error while reading weight: {e}")
            return False


    def _get_weight_value(self):
        try:
            self.serial.write(b'get_weight')
            response = self.serial.readline().decode().strip()
            if response.startswith("KG:"):
                weight_kg = float(response.split(":")[1])
                print(f"[Weight Check] Current weight: {weight_kg:.2f} kg")
                return weight_kg
            else:
                print(f"[Weight Check] Unexpected response: {response}")
                return 0.0
        except Exception as e:
            print(f"[Weight Check] Serial error: {e}")
            return 0.0
        
    def _get_temp_value(self):
        try:
            self.serial.write(b'get_temp')
            response = self.serial.readline().decode().strip()
            if response.startswith("TEMP:"):
                temp_c = float(response.split(":")[1])
                print(f"[Temp Check] Current temperature: {temp_c:.2f} °C")
                return temp_c
            else:
                print(f"[Temp Check] Unexpected response: {response}")
                return 0.0
        except Exception as e:
            print(f"[Temp Check] Serial error: {e}")
            return 0.0
    
    


    


    def read_temperature(self, pi, sensor, target_temp):
        if not ENABLE_HARDWARE:
            print(f"[SIMULATED] Returning fixed GUI-mode temperature: {target_temp + 5}")
            return target_temp + 5  # Simulated temperature for GUI-only testing

        try:
            self.serial.write(b'get_temp\n')
            response = self.serial.readline().decode().strip()
            if response.startswith("TEMP:"):
                float_temp = float(response.split(":")[1])
                print(f"Received temperature: {float_temp:.2f} °C")
                if float_temp >= 450:
                    self.heater_off(self.pi, self.heater_ssr_pin)
                    print(" EMERGENCY: Heater turned OFF due to temperature > 450°C")
                    messagebox.showerror("Overheat Alert", "Temperature exceeded 450°C! Heater has been shut down.")
                return float_temp
            else:
                # print(f"SPI read error. Bytes received: {c}")
            # time.sleep(1)
                print(f"Unexpected temperature response: {response}")
                return 0.0
        except Exception as e:
            print(f"Serial error while reading temperature: {e}")
            return 0.0

        # print("Temperature read timeout. Returning fallback value 0.0")
        # return 0.0

    def read_temperature_average(self, pi, sensor, duration):
        if not ENABLE_HARDWARE:
            print(f"[SIMULATED] Average temperature over {duration}s: 35.0°C")
            return 35.0  # Simulated average for GUI-only mode

        start_time = time.time()
        # stop_time = start_time + duration
        temp_readings = []

        while time.time() - start_time < duration:
            try:
                self.serial.write(b'get_temp\n')
                response = self.serial.readline().decode().strip()
                if response.startswith("TEMP:"):
                    temp = float(response.split(":")[1])
                    temp_readings.append(temp)
                    print(f"Temperature: {temp:.2f}°C")
                else:
                    print(f"Unexpected response: {response}")
            except Exception as e:
                print(f"Serial error while reading temperature: {e}")
                    # print("Bad reading: {:016b}".format(word))
            # else:
                # print("SPI read error. Bytes received:", c)
            time.sleep(0.5)

        if temp_readings:
            avg_temp = sum(temp_readings) / len(temp_readings)
            # print("Average Temperature:", "{:.2f}".format(avg_temp))
            print(f"Average Temperature: {avg_temp:.2f}°C")
            return avg_temp
        else:
            print("No temperature readings recorded. Returning fallback 0.0")
            return 0.0

    def heater_on(self, pi, heater_ssr_pin):
        if ENABLE_HARDWARE:
            pi.write(heater_ssr_pin, 1)
            print("Heater turned on")
        else:
            print("[SIMULATED] Heater ON")

    def heater_off(self, pi, heater_ssr_pin):
        if ENABLE_HARDWARE:
            pi.write(heater_ssr_pin, 0)
            print("Heater turned off")
        else:
            print("[SIMULATED] Heater OFF")

    def initialize_fans_0(self, kit, fan_channels):
        if ENABLE_HARDWARE:
            for channel in fan_channels:
                kit._pca.channels[channel].duty_cycle = 0
        else:
            print("[SIMULATED] Fans set to 0% duty cycle")

    def initialize_fans_100(self, kit, fan_channels):
        if ENABLE_HARDWARE:
            for channel in fan_channels:
                kit._pca.channels[channel].duty_cycle = 100
        else:
            print("[SIMULATED] Fans set to 100% duty cycle")

    def control_fans(self, kit, fan_channels, duty_cycles):
        if ENABLE_HARDWARE:
            for channel, duty_cycle in zip(fan_channels, duty_cycles):
                kit._pca.channels[channel].duty_cycle = int(duty_cycle * 65535 / 100)
        else:
            print("[SIMULATED] Setting fan duty cycles:", duty_cycles)

    def cooling_system_down(self):
        duty_cycles = [50] * 12  # 12 fan channels
        if ENABLE_HARDWARE:
            self.control_fans(self.kit, self.fan_channels, duty_cycles)
        else:
            print("[SIMULATED] Cooling system fans set to 50% duty cycle")
    
    def _update_person_mode_label(self, message):
        if hasattr(self, "person_mode_label"):
            self.person_mode_label.config(text=message)
    
    def activate_safe_mode(self):
        # Disable heater
        if ENABLE_HARDWARE:
            self.heater_off(self.pi, self.heater_ssr_pin)
            self.pi.write(self.door_ssr_pin, 0)  # Unlock the door
            # self.initialize_fans_0(self.kit, self.fan_channels)  # Turn off fans
            self._set_fan_pwm(0)

        for widget in self.winfo_children():
            if isinstance(widget, tk.Label) and widget in [self.logo_label, self.time_label]:
                continue
            widget.destroy()

        # Show Safe Mode screen
        self.safe_mode_frame = tk.Frame(self, bg="#f4e9e1")
        self.safe_mode_frame.pack(expand=True)

        label = tk.Label(
            self.safe_mode_frame,
            text="SAFE MODE ACTIVATED\n\nHeater disabled.\nDoor unlocked.\nFans turned off.",
            font=("DM Sans", 16),
            bg="#f4e9e1",
            justify="center"
        )
        label.pack(pady=40)

        exit_btn = tk.Button(
            self.safe_mode_frame,
            text="Exit to Main Menu",
            font=("DM Sans", 14),
            command=self.exit_safe_mode
        )
        exit_btn.pack(pady=20)
        
    def exit_safe_mode(self):
        # Clear everything on screen
        for widget in self.winfo_children():
            widget.destroy()

        self.running = True
        self.person_running = False

        self.load_main_screen()
        for widget in self.winfo_children():
            print(widget)
        
if __name__ == "__main__":
    app = ThariBakhoorApp()
    app.mainloop()