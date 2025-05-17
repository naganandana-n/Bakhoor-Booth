import time
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from PIL import Image, ImageTk
import threading

ENABLE_HARDWARE = True  # Set to True when running on Raspberry Pi with full setup

if ENABLE_HARDWARE:
    import pigpio
    import RPi.GPIO as GPIO
    import atexit
    from hx711 import HX711
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

            # self.heater_ssr_pin = 4
            self.heater_ssr_pin = 20
            # self.door_ssr_pin = 17
            self.door_ssr_pin = 16
            self.pi.set_mode(self.heater_ssr_pin, pigpio.OUTPUT)
            self.pi.set_mode(self.door_ssr_pin, pigpio.OUTPUT)

            # making the fans on / off instead of PWM
            # self.kit = ServoKit(channels=16)
            # self.fan_channels = list(range(16))
            # self.initialize_fans_0(self.kit, self.fan_channels)
            self.fan_gpio_pin = 21
            self.pi.set_mode(self.fan_gpio_pin, pigpio.OUTPUT)
            self.pi.write(self.fan_gpio_pin, 0)


            # self.hx = HX711(dout_pin=18, pd_sck_pin=15)
            self.hx = HX711(dout_pin=5, pd_sck_pin=6)
            self.initialize_weight()

            self.sensor = self.pi.spi_open(0, 1000000, 0)
            self.read_temperature_average(self.pi, self.sensor, 3)

            atexit.register(self.cleanup_gpio)
        
        else:
            self.pi = None
            self.kit = None
            self.hx = None
            self.sensor = None
            self.heater_ssr_pin = None
            self.door_ssr_pin = None
            self.fan_channels = []

        self.geometry("600x1024")
        self.configure(bg="#f4e9e1")  # Set background color for the entire application
         # Define the hexadecimal color code
        self.custom_color = "#3e2d25"  # Replace this with your desired color code
        # Initialize the style
        self.style = ttk.Style()
        self.style.theme_use('alt')
        # Configure the custom style
        self.style.configure("Custom.Veritcal.TProgressbar", background="#8B5742")
        # Splash screen
        self.splash_screen()

    def splash_screen(self):
        # Load the image
        try:
            image = Image.open("/home/Arbitrary/Downloads/Assets/Splash.jpeg")

            # Convert the image to a Tkinter-compatible format
            tk_image = ImageTk.PhotoImage(image)

            # Create a Label widget to display the image
            self.logo_label = tk.Label(self, image=tk_image, bg="#f4e9e1")  # Store the logo label as an instance variable
            self.logo_label.image = tk_image  # Retain a reference to the image to prevent garbage collection
        except Exception as e:
            print(f"Warning: Splash image could not be loaded: {e}")
            self.logo_label = tk.Label(self, text="Thari Bakhoor", font=("Arial", 32), bg="#f4e9e1")
        self.logo_label.pack(expand=True)
        # Only run fan purge if hardware is enabled
        if ENABLE_HARDWARE:
            # self.initialize_fans_100(self.kit, self.fan_channels)
            GPIO.output(self.fan_gpio_pin, GPIO.HIGH)
        # Simulate splash screen for 3 seconds
        self.after(3000, self.load_main_screen)

    def load_main_screen(self):
        # Stops all the fans
        if ENABLE_HARDWARE:
            # self.initialize_fans_0(self.kit, self.fan_channels)
            GPIO.output(self.fan_gpio_pin, GPIO.LOW)

        # Destroy splash screen widgets
        self.logo_label.destroy()

        # Load main screen widgets
        self.load_logo()
        self.load_date_time()
        self.load_buttons()
        # Schedule updating time every second
        self.update_time()
        
        # Define the function to be run by the thread
        if ENABLE_HARDWARE:
            self.start_weight_check_thread()
        
    def load_logo(self):
        try:
            image1 = Image.open("/home/Arbitrary/Downloads/Assets/Logo.jpeg")
            logo_image = ImageTk.PhotoImage(image1)
            logo_label = tk.Label(self, image=logo_image, bg="#f4e9e1")
            logo_label.image = logo_image
        except Exception as e:
            print(f"Warning: Logo image not loaded: {e}")
            logo_label = tk.Label(self, text="Thari Bakhoor", font=("Arial", 24, "bold"), bg="#f4e9e1")

        logo_label.pack(pady=20)

    def load_date_time(self):
        self.time_label = tk.Label(self, font=("DM Sans", 16), bg="#f4e9e1")  # Set background color for the label
        self.time_label.pack(pady=40)
        self.update_time()

    def update_time(self):
        current_time = datetime.now().strftime("%A, %d %B %Y \n %I:%M:%S %p")
        self.time_label.config(text=current_time)
        self.after(1000, self.update_time)  # Update time every second

    def load_buttons(self):
        # Create a style object
        style = ttk.Style()

        # Configure the font for the buttons
        style.configure("TButton", font=("DM Sans", 14))
        self.load_buttons_frame = tk.Frame(self, bg="#f4e9e1")  # Store the buttons frame as an instance variable
        self.load_buttons_frame.pack(pady=20)

        self.person_button = ttk.Button(self.load_buttons_frame, text="Person", command=self.show_person_screen, width=10, padding=5)
        self.person_button.grid(row=0, column=0, padx=10)

        self.clothes_button = ttk.Button(self.load_buttons_frame, text="Clothes", command=self.show_clothes_screen, width=10, padding=5)
        self.clothes_button.grid(row=0, column=1, padx=10)

        self.surrounding_button = ttk.Button(self.load_buttons_frame, text="Surrounding", command=self.show_surrounding_screen, width=10, padding=5)
        self.surrounding_button.grid(row=0, column=2, padx=10)

        self.Custom_button = ttk.Button(self.load_buttons_frame, text="Custom", command=self.show_custom_screen, width=10, padding=5)
        self.Custom_button.grid(row=1, column=1, padx=10, pady=20)

    def show_person_screen(self):
        # Destroy the buttons frame
        self.load_buttons_frame.destroy()
        self.running = False
        self.person_running = True
        if ENABLE_HARDWARE:
            self.start_person_150_check_thread()

        # Load frames for Heat, Speed, and Time
        self.heat_frame = tk.Frame(self, bg="#f4e9e1")
        self.heat_frame.pack(pady=10)
        self.speed_frame = tk.Frame(self, bg="#f4e9e1")
        self.speed_frame.pack(pady=10)
        self.time_frame = tk.Frame(self, bg="#f4e9e1")
        self.time_frame.pack(pady=0)
        self.button_panel_frame=tk.Frame(self, bg="#f4e9e1")
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
    
        # Define predefined values for the number of filled progress bars and time value
        heat_value = 3
        speed_value = 3
        time_value = 2
    
        # Create and pack progress bars in heat_frame
        self.heat_progress_bars = []
        for i, length in enumerate(bar_lengths):
            progress_bar = ttk.Progressbar(self.heat_frame, orient=tk.VERTICAL, length=length, mode='determinate', style="Custom.Vertical.TProgressbar")
            progress_bar.grid(row=1, column=i, padx=5, sticky="s")  # Align bottom using "s"
            self.heat_progress_bars.append(progress_bar)
    
            # Configure style for individual progress bars
            self.heat_frame.style = ttk.Style()
            self.heat_frame.style.configure("Custom.Vertical.TProgressbar", background="#8B5742")
    
            # Fill progress bars according to heat_value
            if i < heat_value:
                progress_bar["value"] = 100

        # Create and pack progress bars in speed_frame
        self.speed_progress_bars = []
        for i, length in enumerate(bar_lengths):
            progress_bar = ttk.Progressbar(self.speed_frame, orient=tk.VERTICAL, length=length, mode='determinate', style="Custom.Vertical.TProgressbar")
            progress_bar.grid(row=1, column=i, padx=5, sticky="s")  # Align bottom using "s"
            self.speed_progress_bars.append(progress_bar)
    
            # Configure style for individual progress bars
            self.speed_frame.style = ttk.Style()
            self.speed_frame.style.configure("Custom.Vertical.TProgressbar", background="#8B5742")
    
            # Fill progress bars according to speed_value
            if i < speed_value:
                progress_bar["value"] = 100
    
        hours = int(time_value / 60)
        minutes = int(time_value % 60)
        seconds = 0  # Since you are formatting only minutes initially
        time_text = "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
        
        # Display the formatted time_value in the time_record label
        self.time_record = tk.Label(self.time_frame, text=time_text, bg="#f4e9e1", font=("DM Sans", 12))
        self.time_record.grid(row=1, column=2, sticky="w")

        # Create Save button to print values
        save_button = tk.Button(self.button_panel_frame, text="Start", command=self.save_values, font=("DM Sans", 12))
        save_button.grid(row=0, column=0, padx=(50, 10), pady=(10, 0)) # Place the Save button on the left

        # Create Close button
        close_button = tk.Button(self.button_panel_frame, text="Close", command=self.show_main_screen_buttons, font=("DM Sans", 12))
        close_button.grid(row=0, column=2, padx=(10, 50), pady=(10, 0))  # Place the Close button on the right

    def show_clothes_screen(self):
        self.running=False

        # Destroy the buttons frame
        self.load_buttons_frame.destroy()
    
        # Load frames for Heat, Speed, and Time
        self.heat_frame = tk.Frame(self, bg="#f4e9e1")
        self.heat_frame.pack(pady=10)
        self.speed_frame = tk.Frame(self, bg="#f4e9e1")
        self.speed_frame.pack(pady=10)
        self.time_frame = tk.Frame(self, bg="#f4e9e1")
        self.time_frame.pack(pady=0)
        self.button_panel_frame=tk.Frame(self, bg="#f4e9e1")
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
    
        # Define predefined values for the number of filled progress bars and time value
        heat_value = 1
        speed_value = 2
        time_value = 3
    
        # Create and pack progress bars in heat_frame
        self.heat_progress_bars = []
        for i, length in enumerate(bar_lengths):
            progress_bar = ttk.Progressbar(self.heat_frame, orient=tk.VERTICAL, length=length, mode='determinate', style="Custom.Vertical.TProgressbar")
            progress_bar.grid(row=1, column=i, padx=5, sticky="s")  # Align bottom using "s"
            self.heat_progress_bars.append(progress_bar)
    
            # Configure style for individual progress bars
            self.heat_frame.style = ttk.Style()
            self.heat_frame.style.configure("Custom.Vertical.TProgressbar", background="#8B5742")
    
            # Fill progress bars according to heat_value
            if i < heat_value:
                progress_bar["value"] = 100

        # Create and pack progress bars in speed_frame
        self.speed_progress_bars = []
        for i, length in enumerate(bar_lengths):
            progress_bar = ttk.Progressbar(self.speed_frame, orient=tk.VERTICAL, length=length, mode='determinate', style="Custom.Vertical.TProgressbar")
            progress_bar.grid(row=1, column=i, padx=5, sticky="s")  # Align bottom using "s"
            self.speed_progress_bars.append(progress_bar)
    
            # Configure style for individual progress bars
            self.speed_frame.style = ttk.Style()
            self.speed_frame.style.configure("Custom.Vertical.TProgressbar", background="#8B5742")
    
            # Fill progress bars according to speed_value
            if i < speed_value:
                progress_bar["value"] = 100
    
        hours = int(time_value / 60)
        minutes = int(time_value % 60)
        seconds = 0  # Since you are formatting only minutes initially
        time_text = "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
    
        # Display the formatted time_value in the time_record label
        self.time_record = tk.Label(self.time_frame, text=time_text, bg="#f4e9e1", font=("DM Sans", 12))
        self.time_record.grid(row=1, column=2, sticky="w")

        # Create Save button to print values
        save_button = tk.Button(self.button_panel_frame, text="Start", command=self.save_values, font=("DM Sans", 12))
        save_button.grid(row=0, column=0, padx=(50, 10), pady=(10, 0)) # Place the Save button on the left

        # Create Close button
        close_button = tk.Button(self.button_panel_frame, text="Close", command=self.show_main_screen_buttons, font=("DM Sans", 12))
        close_button.grid(row=0, column=2, padx=(10, 50), pady=(10, 0))  # Place the Close button on the right


    def show_surrounding_screen(self):
        self.running=False
        # Destroy the buttons frame
        self.load_buttons_frame.destroy()
    
        # Load frames for Heat, Speed, and Time
        self.heat_frame = tk.Frame(self, bg="#f4e9e1")
        self.heat_frame.pack(pady=10)
        self.speed_frame = tk.Frame(self, bg="#f4e9e1")
        self.speed_frame.pack(pady=10)
        self.time_frame = tk.Frame(self, bg="#f4e9e1")
        self.time_frame.pack(pady=0)
        self.button_panel_frame=tk.Frame(self, bg="#f4e9e1")
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
    
        # Define predefined values for the number of filled progress bars and time value
        heat_value = 2
        speed_value = 1
        time_value = 4
    
        # Create and pack progress bars in heat_frame
        self.heat_progress_bars = []
        for i, length in enumerate(bar_lengths):
            progress_bar = ttk.Progressbar(self.heat_frame, orient=tk.VERTICAL, length=length, mode='determinate', style="Custom.Vertical.TProgressbar")
            progress_bar.grid(row=1, column=i, padx=5, sticky="s")  # Align bottom using "s"
            self.heat_progress_bars.append(progress_bar)
    
            # Configure style for individual progress bars
            self.heat_frame.style = ttk.Style()
            self.heat_frame.style.configure("Custom.Vertical.TProgressbar", background="#8B5742")
    
            # Fill progress bars according to heat_value
            if i < heat_value:
                progress_bar["value"] = 100

        # Create and pack progress bars in speed_frame
        self.speed_progress_bars = []
        for i, length in enumerate(bar_lengths):
            progress_bar = ttk.Progressbar(self.speed_frame, orient=tk.VERTICAL, length=length, mode='determinate', style="Custom.Vertical.TProgressbar")
            progress_bar.grid(row=1, column=i, padx=5, sticky="s")  # Align bottom using "s"
            self.speed_progress_bars.append(progress_bar)
    
            # Configure style for individual progress bars
            self.speed_frame.style = ttk.Style()
            self.speed_frame.style.configure("Custom.Vertical.TProgressbar", background="#8B5742")
    
            # Fill progress bars according to speed_value
            if i < speed_value:
                progress_bar["value"] = 100
    
        hours = int(time_value / 60)
        minutes = int(time_value % 60)
        seconds = 0  # Since you are formatting only minutes initially
        time_text = "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
 
        # Display the formatted time_value in the time_record label
        self.time_record = tk.Label(self.time_frame, text=time_text, bg="#f4e9e1", font=("DM Sans", 12))
        self.time_record.grid(row=1, column=2, sticky="w")

        # Create Save button to print values
        save_button = tk.Button(self.button_panel_frame, text="Start", command=self.save_values, font=("DM Sans", 12))
        save_button.grid(row=0, column=0, padx=(50, 10), pady=(10, 0)) # Place the Save button on the left

        # Create Close button
        close_button = tk.Button(self.button_panel_frame, text="Close", command=self.show_main_screen_buttons, font=("DM Sans", 12))
        close_button.grid(row=0, column=2, padx=(10, 50), pady=(10, 0))  # Place the Close button on the right
        
    def save_values(self):
        # Notes down the time at when the process starts
        self.saved_time = time.time()

        # Print the values of the filled progress bars in heat_frame
        heat_value = sum(pb["value"] == 100 for pb in self.heat_progress_bars)
        print("Heat:", heat_value)

        # Print the values of the filled progress bars in speed_frame
        speed_value = sum(pb["value"] == 100 for pb in self.speed_progress_bars)
        print("Speed:", speed_value)

        # Get the time value from self.time_record
        time_value = self.get_time_value()
        print("Time:", time_value)
        self.assigned_heat = heat_value
        self.assigned_speed = speed_value
        self.assigned_time = time_value

        self.time_frame.destroy()
        self.heat_frame.destroy()
        self.speed_frame.destroy()
        self.button_panel_frame.destroy()
        
        # Heating element is turned on. 
        if ENABLE_HARDWARE:
            self.heater_on(self.pi, self.heater_ssr_pin)
        self.waiting_screen()

    # Autostart function that saved values to be used in the next screen
    def auto_start_save(self):
            self.running = False
            self.person_running = True
            if ENABLE_HARDWARE:
                self.start_person_150_check_thread()
            self.saved_time = time.time()
            print("AutoStart heat:", self.assigned_heat)
            print("Autostart Speed:", self.assigned_speed)
            print("Autostart Time", self.assigned_time)

            self.load_buttons_frame.destroy()
            self.waiting_screen()
            

    # Assigns temperature based on the levels of progress bars in the heat frame
    def check_heat_value(self):
        if self.assigned_heat == 1:
            self.assigned_heat = 80
        elif self.assigned_heat == 2:
            self.assigned_heat = 100    
        elif self.assigned_heat == 3:
            self.assigned_heat = 125
        elif self.assigned_heat == 4:
            self.assigned_heat = 150
        else:
            self.assigned_heat = 170
        return self.assigned_heat
    
    '''
    # Assigns speed based on the levels of progress bars in the speed frame
    # duty_cycles[0] is made forthe main fan 90 x90 
    def check_speed_value(self):
        if self.assigned_speed == 1:
            duty_cycles = [25, 0, 100, 25, 75, 50, 0, 60, 30, 90, 100, 0]
        elif self.assigned_speed == 2:
            duty_cycles = [25, 0, 100, 25, 75, 0, 40, 60, 30, 90, 100, 0]
        elif self.assigned_speed == 3:
            duty_cycles = [25, 100, 100, 0, 75, 100, 40, 60, 30, 90, 100, 0]
        elif self.assigned_speed == 4:
            duty_cycles = [25, 0, 100, 0, 75, 50, 40, 60, 30, 90, 100, 0]
        else:
            duty_cycles = [25, 0, 0, 25, 75, 0, 0, 60, 30, 90, 100, 0]
        return duty_cycles
    '''
    
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
                temperature = self.read_temperature(self.pi, self.sensor, target_temp)
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
                    temperature = self.read_temperature(self.pi, self.sensor, self.targettemp[1])
                    if temperature is not None:
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
        if self.person_running == True:
                self.stop_weight_150_check_thread()
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
                temperature = self.read_temperature(self.pi, self.sensor, self.targettemp[0])
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
        if ENABLE_HARDWARE:
            self.start_person_150_check_thread()

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

        # Create Save button to print values
        save_button = tk.Button(self.button_panel_frame, text="Start", command=self.save_values if ENABLE_HARDWARE else self.custom_save_values, font=("DM Sans", 12))
        save_button.grid(row=0, column=0, padx=(50, 10), pady=(10, 0))  # Place the Save button on the left

        # Create Close button
        close_button = tk.Button(self.button_panel_frame, text="Close", command=self.show_main_screen_buttons, font=("DM Sans", 12))
        close_button.grid(row=0, column=2, padx=(10, 50), pady=(10, 0))  # Place the Close button on the right


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

        # Reload the main screen buttons
        self.load_logo()
        self.load_date_time()
        self.load_buttons()
    
        self.running = True
        self.person_running = False

        if ENABLE_HARDWARE:
            self.stop_weight_150_check_thread()
            self.start_weight_check_thread()

    def cleanup_gpio(self):
        if ENABLE_HARDWARE:
            # Turn off all heaters
            self.heater_off(self.pi, self.heater_ssr_pin)
            # Turn off all fans
            # self.initialize_fans_0(self.kit, self.fan_channels)
            GPIO.output(self.self.fan_gpio_pin, GPIO.LOW)
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

    def check_150_weight(self): 
        if ENABLE_HARDWARE:
            weight_safe = self.checking_150_weight()
            if weight_safe:
                print("Weight more than 150kg")
                self.pi.write(self.door_ssr_pin, 1)
            else:
                print("Weight less than 150kg")
                self.pi.write(self.door_ssr_pin, 0)
        else:
            print("[GUI-only] Skipping 150kg weight check.")

    def initialize_weight(self):
        if ENABLE_HARDWARE:
            self.hx.reset()
            self.hx.zero()
            ratio = 21.81341463414634
            self.hx.set_scale_ratio(ratio)
            time.sleep(1)
            weight_ini = self.hx.get_weight_mean()
            print(weight_ini)
            time.sleep(5)
        else:
            print("[GUI-only] Skipping load cell initialization.")

    def checking_weight(self):
        if not ENABLE_HARDWARE:
            print("[GUI-only] Skipping weight check. Returning False.")
            return False

        weight_duration = 10  # Adjust as needed
        start_time = time.time()
        weights = []

        while time.time() - start_time < weight_duration:
            if not self.running:
                print("Weight check interrupted by user")
                return False
            weight = self.hx.get_weight_mean()
            weight_kg = max(weight / 1000.00, 0.00)
            print(f"Weight: {weight_kg:.2f} kg")
            weights.append(weight_kg)
            time.sleep(0.5)

        average_weight = sum(weights) / len(weights)
        print(average_weight)
        return average_weight > 4.00  # Return True if weight is safe

    def checking_150_weight(self):
        if not ENABLE_HARDWARE:
            print("[GUI-only] Skipping 150kg weight check. Returning False.")
            return False

        weight_duration = 10  # Adjust as needed
        start_time = time.time()
        weights = []

        while time.time() - start_time < weight_duration:
            if not self.person_running:
                print("Weight check interrupted by user")
                return False
            weight = self.hx.get_weight_mean()
            weight_kg = max(weight / 1000.00, 0.00)
            print(f"Weight: {weight_kg:.2f} kg")
            weights.append(weight_kg)
            time.sleep(0.5)

        average_weight = sum(weights) / len(weights)
        print(average_weight)
        return average_weight > 6.00  # Return True if weight is safe

    def schedule_weight_check(self):
        if not ENABLE_HARDWARE:
            print("[GUI-only] Weight check scheduling skipped.")
            return
        self.check_person_weight()
        self.after(2000, self.schedule_weight_check)

    def start_weight_check_thread(self):
        if not ENABLE_HARDWARE:
            print("[GUI-only] Skipping start_weight_check_thread.")
            return

        # Define the function to be run by the thread
        def weight_check_thread_func():
            while self.running:
                self.check_person_weight()
                time.sleep(2)

        self.weight_check_thread = threading.Thread(target=weight_check_thread_func)
        self.weight_check_thread.daemon = True
        self.weight_check_thread.start()

    def start_person_150_check_thread(self):
        if not ENABLE_HARDWARE:
            print("[GUI-only] Skipping start_person_150_check_thread.")
            return

        def person_check_thread_func():
            while self.person_running:
                self.check_150_weight()
                time.sleep(2)

        self.weight_150_check_thread = threading.Thread(target=person_check_thread_func)
        self.weight_150_check_thread.daemon = True
        self.weight_150_check_thread.start()

    def stop_weight_check_thread(self):
        self.running = False
        if not ENABLE_HARDWARE:
            print("[GUI-only] Skipping stop_weight_check_thread.")
            return
        if self.weight_check_thread and self.weight_check_thread.is_alive():
            self.weight_check_thread.join()

    def stop_weight_150_check_thread(self):
        self.person_running = False
        if not ENABLE_HARDWARE:
            print("[GUI-only] Skipping stop_weight_150_check_thread.")
            return
        if hasattr(self, 'weight_150_check_thread') and self.weight_150_check_thread and self.weight_150_check_thread.is_alive():
            self.weight_150_check_thread.join()

    def is_weight_check_thread_running(self):
        if not ENABLE_HARDWARE:
            return False
        return hasattr(self, 'weight_check_thread') and self.weight_check_thread and self.weight_check_thread.is_alive()


    def read_temperature(self, pi, sensor, target_temp):
        if not ENABLE_HARDWARE:
            print(f"[SIMULATED] Returning fixed GUI-mode temperature: {target_temp + 5}")
            return target_temp + 5  # Simulated temperature for GUI-only testing

        stop_time = time.time() + 600  # Set a 10-min timeout
        float_temp = 0.0

        while time.time() < stop_time and float_temp < target_temp:
            c, d = pi.spi_read(sensor, 2)
            if c == 2:
                word = (d[0] << 8) | d[1]
                if (word & 0x8006) == 0:
                    t = (word >> 3) / 4.0
                    float_temp = t
                    print("Raw Thermocouple Reading:", word)
                    print("Temperature (t):", t)
                    print("Formatted Temperature (float_temp):", float_temp)
                    print("Current Temp:", "{:.2f}".format(float_temp))
                    return float_temp
                else:
                    print(f"Bad reading: {word:016b}")
            else:
                print(f"SPI read error. Bytes received: {c}")
            time.sleep(1)

        print("Temperature read timeout. Returning fallback value 0.0")
        return 0.0

    def read_temperature_average(self, pi, sensor, duration):
        if not ENABLE_HARDWARE:
            print(f"[SIMULATED] Average temperature over {duration}s: 35.0°C")
            return 35.0  # Simulated average for GUI-only mode

        start_time = time.time()
        stop_time = start_time + duration
        temp_readings = []

        while time.time() < stop_time:
            c, d = pi.spi_read(sensor, 2)
            if c == 2:
                word = (d[0] << 8) | d[1]
                if (word & 0x8006) == 0:
                    t = (word >> 3) / 4.0
                    temp_readings.append(t)
                    print("Current Temp:", "{:.2f}".format(t))
                else:
                    print("Bad reading: {:016b}".format(word))
            else:
                print("SPI read error. Bytes received:", c)
            time.sleep(0.5)

        if temp_readings:
            avg_temp = sum(temp_readings) / len(temp_readings)
            print("Average Temperature:", "{:.2f}".format(avg_temp))
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
        
if __name__ == "__main__":
    app = ThariBakhoorApp()
    app.mainloop()