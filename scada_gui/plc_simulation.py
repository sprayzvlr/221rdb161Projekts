import tkinter as tk
import time
from model.predict import predict
import tkinter as tk
from tkinter import ttk
import random
import time
import threading
from datetime import datetime

class PLCSimulation:
    def __init__(self, root=None):
        # Create a new window if no root is provided
        if root is None:
            self.window = tk.Toplevel()
            self.window.title("PLC Simulācija")
            self.window.geometry("700x500")
            self.window.minsize(600, 400)
        else:
            self.window = root
            
        # PLC status variables
        self.running = False
        self.thread = None
        self.status = "Gaidstāve"
        self.cycle_count = 0
        self.start_time = None
        self.anomaly_detected = False
        
        # Digitālās ieejas (slēdži un sensori)
        self.inputs = {
            "Sistēmas ieslēgšana": False,
            "Sildītāja drošības relejs": False, 
            "Dzesētāja drošības relejs": False,
            "Ārkārtas apturēšana": False
        }
        
        # Digitālās izejas (izpildmehānismi)
        self.outputs = {
            "Sildītāja relejs": False, 
            "Dzesētāja relejs": False, 
            "Cirkulācijas sūknis": False,
            "Avārijas signalizācija": False
        }
        
        # Kontroles flags
        self.memory = {
            "Sildīšanas režīms": False, 
            "Dzesēšanas režīms": False, 
            "Automātiskais režīms": False,
            "Trauksmes režīms": False
        }
        
        # Analogās ieejas (temperatūras sensori)
        self.analog_inputs = {
            "Telpas temperatūra": 22.0,  # °C
            "Sildītāja temperatūra": 40.0,  # °C 
            "Dzesētāja temperatūra": 18.0   # °C
        }
        
        # Analogās izejas (kontroles signāli)
        self.analog_outputs = {
            "Sildītāja jauda": 0,  # %
            "Dzesētāja jauda": 0,  # %
            "Ventilatora ātrums": 0  # %
        }
        
        # Iestatītās vērtības
        self.set_point = 22.0  # Mērķa temperatūra (°C)
        
        # Create the UI
        self._create_ui()
    
    def _create_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Sildīšanas-Dzesēšanas Sistēmas PLC", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)
        
        # Control frame (left side)
        control_frame = ttk.LabelFrame(main_frame, text="Vadība", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Status section
        status_frame = ttk.Frame(control_frame)
        status_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.status_label = ttk.Label(status_frame, text=self.status, font=("Arial", 10, "bold"))
        self.status_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(status_frame, text="Cikli:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.cycle_label = ttk.Label(status_frame, text="0")
        self.cycle_label.grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(status_frame, text="Darbības laiks:").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.runtime_label = ttk.Label(status_frame, text="00:00:00")
        self.runtime_label.grid(row=2, column=1, sticky=tk.W)
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Sākt", command=self.start_plc)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Apturēt", command=self.stop_plc, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = ttk.Button(button_frame, text="Atiestatīt", command=self.reset_plc)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        # Digital I/O frame (right side)
        io_frame = ttk.LabelFrame(main_frame, text="I/O Stāvoklis", padding=10)
        io_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Input section
        input_frame = ttk.LabelFrame(io_frame, text="Vadības un drošības slēdži", padding=5)
        input_frame.pack(fill=tk.X, pady=5)
        
        self.input_vars = {}
        row = 0
        for input_name in self.inputs:
            self.input_vars[input_name] = tk.BooleanVar(value=self.inputs[input_name])
            
            # Pievieno papildu skaidrojumu drošības relejiem
            if "drošības relejs" in input_name:
                text = f"{input_name} (⚠️ ja ieslēgts = bloķēts)"
                fg_color = "darkred"
            else:
                text = input_name
                fg_color = "black"
                
            cb = ttk.Checkbutton(input_frame, text=text, variable=self.input_vars[input_name],
                               command=lambda name=input_name: self.toggle_input(name))
            cb.grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
            
            # Uzstādīt krāsu (dažos ttk motīvos tas var nedarboties)
            try:
                cb.configure(foreground=fg_color)
            except:
                pass
                
            row += 1
        
        # Output section
        output_frame = ttk.LabelFrame(io_frame, text="Izpildmehānismi", padding=5)
        output_frame.pack(fill=tk.X, pady=5)
        
        self.output_indicators = {}
        row = 0
        for output_name in self.outputs:
            indicator = ttk.Label(output_frame, text="○", font=("Arial", 12), foreground="gray")
            indicator.grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
            ttk.Label(output_frame, text=output_name).grid(row=row, column=1, sticky=tk.W)
            self.output_indicators[output_name] = indicator
            row += 1
        
        # Analog section
        analog_frame = ttk.LabelFrame(io_frame, text="Temperatūras un kontroles vērtības", padding=5)
        analog_frame.pack(fill=tk.X, pady=5)
        
        # Set point control
        set_point_frame = ttk.Frame(analog_frame)
        set_point_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        
        ttk.Label(set_point_frame, text="Mērķa temperatūra:").pack(side=tk.LEFT, padx=5)
        self.set_point_var = tk.DoubleVar(value=self.set_point)
        set_point_slider = ttk.Scale(set_point_frame, from_=15, to=30, orient=tk.HORIZONTAL, 
                                   length=150, variable=self.set_point_var,
                                   command=self.update_set_point)
        set_point_slider.pack(side=tk.LEFT, padx=5)
        
        self.set_point_label = ttk.Label(set_point_frame, text=f"{self.set_point:.1f} °C")
        self.set_point_label.pack(side=tk.LEFT, padx=5)
        
        # Analog inputs
        row = 1
        self.analog_sliders = {}
        self.analog_labels = {}  # Dictionary to store label references
        
        # Sensoru vērtības
        inputs_frame = ttk.LabelFrame(analog_frame, text="Sensori")
        inputs_frame.grid(row=row, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        row += 1
        
        inner_row = 0
        for ai_name in self.analog_inputs:
            # Temperatūru slaideri
            unit = "°C" if "temperatūra" in ai_name.lower() else "%"
            min_val = 0
            max_val = 40
            
            if "sildītāja" in ai_name.lower():
                min_val = 20
                max_val = 80
            elif "dzesētāja" in ai_name.lower():
                min_val = 5
                max_val = 30
            
            ttk.Label(inputs_frame, text=f"{ai_name}:").grid(row=inner_row, column=0, sticky=tk.W, padx=5, pady=2)
            slider = ttk.Scale(inputs_frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL, length=150,
                              command=lambda v, name=ai_name: self.update_analog_input(name, v))
            
            # Iestatīt slaidera sākotnējo vērtību
            slider.set(self.analog_inputs[ai_name])
            slider.grid(row=inner_row, column=1, padx=5, pady=2)
            self.analog_sliders[ai_name] = slider
            
            value_label = ttk.Label(inputs_frame, text=f"{self.analog_inputs[ai_name]:.1f} {unit}")
            value_label.grid(row=inner_row, column=2, padx=5, pady=2)
            
            # Store the value label in dictionary
            self.analog_labels[ai_name] = value_label
            inner_row += 1
        
        # Analog outputs with proper units
        outputs_frame = ttk.LabelFrame(analog_frame, text="Izpildmehānismu vadība")
        outputs_frame.grid(row=row, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        
        self.analog_output_progress = {}
        self.analog_output_labels = {}
        
        inner_row = 0
        for ao_name in self.analog_outputs:
            unit = "%" 
            ttk.Label(outputs_frame, text=f"{ao_name}:").grid(row=inner_row, column=0, sticky=tk.W, padx=5, pady=2)
            progress = ttk.Progressbar(outputs_frame, length=150, mode='determinate', maximum=100)
            progress.grid(row=inner_row, column=1, padx=5, pady=2)
            
            value_label = ttk.Label(outputs_frame, text=f"{self.analog_outputs[ao_name]:.1f} {unit}")
            value_label.grid(row=inner_row, column=2, padx=5, pady=2)
            
            # Store references in dictionaries for updates
            self.analog_output_progress[ao_name] = progress
            self.analog_output_labels[ao_name] = value_label
            inner_row += 1
        
        # Logs frame
        log_frame = ttk.LabelFrame(main_frame, text="PLC žurnāls", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = tk.Text(log_frame, height=8, width=70, wrap=tk.WORD)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Add initial log message
        self.log_message("PLC simulācija inicializēta")
        
        # Update interval for runtime display (ms)
        self.update_interval = 1000
        self.window.after(self.update_interval, self.update_runtime)
    
    def toggle_input(self, input_name):
        """Digitālās ieejas izmaiņas"""
        self.inputs[input_name] = self.input_vars[input_name].get()
        
        # Konkrēti paziņojumi atkarībā no slēdža
        if input_name == "Sistēmas ieslēgšana":
            action = "Sistēma ieslēgta" if self.inputs[input_name] else "Sistēma izslēgta"
        elif input_name == "Ārkārtas apturēšana":
            action = "ĀRKĀRTAS APTURĒŠANA AKTIVIZĒTA!" if self.inputs[input_name] else "Ārkārtas apturēšana atcelta"
        elif "drošības" in input_name.lower():
            device = "sildītāja" if "sildītāja" in input_name.lower() else "dzesētāja"
            if self.inputs[input_name]:
                action = f"DROŠĪBAS SIGNĀLS: {device.capitalize()} bloķēts!"
                
                # Nekavējoties apturēt attiecīgo iekārtu
                if "sildītāja" in input_name.lower():
                    self.update_output("Sildītāja relejs", False)
                    self.update_analog_output("Sildītāja jauda", 0)
                else:
                    self.update_output("Dzesētāja relejs", False)
                    self.update_analog_output("Dzesētāja jauda", 0)
                
                # Ieslēgt avārijas signalizāciju
                self.update_output("Avārijas signalizācija", True)
            else:
                action = f"{device.capitalize()} drošības signāls atcelts - iekārta atbloķēta"
                # Atcelt avārijas signalizāciju, ja abi signāli ir atcelti
                if not self.inputs["Sildītāja drošības relejs"] and not self.inputs["Dzesētāja drošības relejs"]:
                    self.update_output("Avārijas signalizācija", False)
        else:
            action = f"{input_name} = {'IESLĒGTS' if self.inputs[input_name] else 'IZSLĒGTS'}"
            
        self.log_message(action)
    
    def update_set_point(self, value):
        """Atjaunina mērķa temperatūru"""
        value = float(value)
        self.set_point = value
        self.set_point_label.config(text=f"{value:.1f} °C")
        self.log_message(f"Mērķa temperatūra iestatīta uz {value:.1f} °C")
    
    def update_analog_input(self, input_name, value):
        """Atjaunina analogās ieejas vērtību"""
        value = float(value)
        self.analog_inputs[input_name] = value
        
        # Pievieno mērvienību atkarībā no parametra
        unit = "°C" if "temperatūra" in input_name.lower() else "%"
        
        if input_name in self.analog_labels:
            self.analog_labels[input_name].config(text=f"{value:.1f} {unit}")
    
    def update_output(self, output_name, value):
        self.outputs[output_name] = value
        indicator = self.output_indicators[output_name]
        if value:
            indicator.config(text="●", foreground="green")
        else:
            indicator.config(text="○", foreground="gray")
    
    def update_analog_output(self, output_name, value):
        """Atjaunina analogās izejas vērtību"""
        self.analog_outputs[output_name] = value
        
        # Pievieno mērvienību
        unit = "%"
        
        if output_name in self.analog_output_progress:
            self.analog_output_progress[output_name]["value"] = value
        if output_name in self.analog_output_labels:
            self.analog_output_labels[output_name].config(text=f"{value:.1f} {unit}")
    
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)  # Scroll to the end
    
    def start_plc(self):
        if not self.running:
            self.running = True
            self.start_time = time.time()
            self.status = "Aktīvs"
            self.status_label.config(text=self.status)
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.log_message("PLC darbība uzsākta")
            
            # Start the PLC execution thread
            self.thread = threading.Thread(target=self.plc_cycle, daemon=True)
            self.thread.start()
    
    def stop_plc(self):
        if self.running:
            self.running = False
            self.status = "Apturēts"
            self.status_label.config(text=self.status)
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.log_message("PLC darbība apturēta")
    
    def reset_plc(self):
        self.stop_plc()
        
        # Reset all variables
        self.cycle_count = 0
        self.cycle_label.config(text="0")
        self.runtime_label.config(text="00:00:00")
        self.anomaly_detected = False
        
        # Atiestatīt iestatītās vērtības
        self.set_point = 22.0
        self.set_point_var.set(22.0)
        self.set_point_label.config(text=f"{self.set_point:.1f} °C")
        
        # Reset inputs and outputs
        for input_name in self.inputs:
            self.inputs[input_name] = False
            self.input_vars[input_name].set(False)
        
        for output_name in self.outputs:
            self.update_output(output_name, False)
        
        # Atiestatīt analogās ieejas uz piemērotām sākuma vērtībām
        default_values = {
            "Telpas temperatūra": 22.0,
            "Sildītāja temperatūra": 40.0,
            "Dzesētāja temperatūra": 18.0
        }
        
        for ai_name in self.analog_inputs:
            default_value = default_values.get(ai_name, 0)
            self.analog_inputs[ai_name] = default_value
            self.analog_sliders[ai_name].set(default_value)
            
            unit = "°C" if "temperatūra" in ai_name.lower() else "%"
            if ai_name in self.analog_labels:
                self.analog_labels[ai_name].config(text=f"{default_value:.1f} {unit}")
        
        # Atiestatīt analogās izejas
        for ao_name in self.analog_outputs:
            self.update_analog_output(ao_name, 0)
        
        # Reset status
        self.status = "Atiestatīts"
        self.status_label.config(text=self.status)
        
        # Clear log but add reset message
        self.log_text.delete(1.0, tk.END)
        self.log_message("PLC atiestatīts")
    
    def update_runtime(self):
        if self.running and self.start_time:
            elapsed = time.time() - self.start_time
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            
            runtime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.runtime_label.config(text=runtime_str)
        
        # Schedule the next update
        self.window.after(self.update_interval, self.update_runtime)
    
    def plc_cycle(self):
        """Galvenais PLC izpildes cikls"""
        while self.running:
            # Palielina ciklu skaitītāju
            self.cycle_count += 1
            self.window.after(0, lambda: self.cycle_label.config(text=str(self.cycle_count)))
            
            # Pārbauda ārkārtas stāvokli
            emergency_stop = self.inputs["Ārkārtas apturēšana"]
            
            if emergency_stop:
                # Ārkārtas apturēšanas gadījumā izslēdz visu
                self.window.after(0, lambda: self.update_output("Sildītāja relejs", False))
                self.window.after(0, lambda: self.update_output("Dzesētāja relejs", False))
                self.window.after(0, lambda: self.update_output("Cirkulācijas sūknis", False))
                self.window.after(0, lambda: self.update_output("Avārijas signalizācija", True))
                
                # Atjaunina analogās izejas
                self.window.after(0, lambda: self.update_analog_output("Sildītāja jauda", 0))
                self.window.after(0, lambda: self.update_analog_output("Dzesētāja jauda", 0))
                self.window.after(0, lambda: self.update_analog_output("Ventilatora ātrums", 0))
                
                # Gaidīt nākamo ciklu
                time.sleep(0.5)
                continue
            
            # Ja sistēma nav ieslēgta, nedarbojas
            if not self.inputs["Sistēmas ieslēgšana"]:
                self.window.after(0, lambda: self.update_output("Sildītāja relejs", False))
                self.window.after(0, lambda: self.update_output("Dzesētāja relejs", False))
                self.window.after(0, lambda: self.update_output("Cirkulācijas sūknis", False))
                self.window.after(0, lambda: self.update_output("Avārijas signalizācija", False))
                
                # Atjaunina analogās izejas
                self.window.after(0, lambda: self.update_analog_output("Sildītāja jauda", 0))
                self.window.after(0, lambda: self.update_analog_output("Dzesētāja jauda", 0))
                self.window.after(0, lambda: self.update_analog_output("Ventilatora ātrums", 0))
                
                # Gaidīt nākamo ciklu
                time.sleep(0.5)
                continue
            
            # Iegūst pašreizējās temperatūras
            current_temp = self.analog_inputs["Telpas temperatūra"]
            heater_temp = self.analog_inputs["Sildītāja temperatūra"]
            cooler_temp = self.analog_inputs["Dzesētāja temperatūra"]
            
            # Temperatūras starpība (cik tālu esam no mērķa)
            temp_diff = self.set_point - current_temp
            
            # Sildīšanas/dzesēšanas loģika ar drošībām
            heating_mode = temp_diff > 0.5  # Vajag sildīt
            cooling_mode = temp_diff < -0.5  # Vajag dzesēt
            
            # Cirkulācijas sūkņa loģika - ieslēgts, kad sistēma darbojas
            self.window.after(0, lambda: self.update_output("Cirkulācijas sūknis", True))
            
            # Anomāliju pārbaude - pārāk liela temperatūras starpība starp sildītāju un telpu
            temp_diff_heater = abs(heater_temp - current_temp)
            is_anomaly = temp_diff_heater > 30  # Pārāk liela starpība
            
            if is_anomaly and not self.anomaly_detected:
                self.anomaly_detected = True
                self.window.after(0, lambda: self.log_message("⚠️ ANOMĀLIJA - pārāk liela temperatūras starpība!"))
                self.window.after(0, lambda: self.update_output("Avārijas signalizācija", True))
            elif not is_anomaly and self.anomaly_detected:
                self.anomaly_detected = False
                self.window.after(0, lambda: self.log_message("✓ Normāla darbība atjaunota"))
                self.window.after(0, lambda: self.update_output("Avārijas signalizācija", False))
            
            # Drošības releju pārbaude
            heater_safety_active = self.inputs["Sildītāja drošības relejs"]
            cooler_safety_active = self.inputs["Dzesētāja drošības relejs"]
            
            # Sildītāja vadības loģika
            if heating_mode and not heater_safety_active and not is_anomaly:
                # Ieslēdz sildītāju un aprēķina jaudu
                self.window.after(0, lambda: self.update_output("Sildītāja relejs", True))
                self.window.after(0, lambda: self.update_output("Dzesētāja relejs", False))
                
                # Sildītāja jauda proporcionāla temperatūras starpībai
                heater_power = min(100, max(20, abs(temp_diff) * 20))
                self.window.after(0, lambda p=heater_power: self.update_analog_output("Sildītāja jauda", p))
                self.window.after(0, lambda: self.update_analog_output("Dzesētāja jauda", 0))
                
                # Ventilatora ātrums proporcionāls sildītāja jaudai
                fan_speed = min(100, max(30, heater_power * 0.8))
                self.window.after(0, lambda s=fan_speed: self.update_analog_output("Ventilatora ātrums", s))
                
                # Atjaunina status
                self.memory["Sildīšanas režīms"] = True
                self.memory["Dzesēšanas režīms"] = False
                
                if self.cycle_count % 10 == 0:  # Lai neaizvērstu žurnālu
                    self.window.after(0, lambda: self.log_message(f"Sildīšanas režīms, jauda: {heater_power:.1f}%"))
                
            # Dzesētāja vadības loģika
            elif cooling_mode and not cooler_safety_active and not is_anomaly:
                # Ieslēdz dzesētāju un aprēķina jaudu
                self.window.after(0, lambda: self.update_output("Sildītāja relejs", False))
                self.window.after(0, lambda: self.update_output("Dzesētāja relejs", True))
                
                # Dzesētāja jauda proporcionāla temperatūras starpībai
                cooler_power = min(100, max(20, abs(temp_diff) * 20))
                self.window.after(0, lambda: self.update_analog_output("Sildītāja jauda", 0))
                self.window.after(0, lambda p=cooler_power: self.update_analog_output("Dzesētāja jauda", p))
                
                # Ventilatora ātrums proporcionāls dzesētāja jaudai
                fan_speed = min(100, max(30, cooler_power * 0.8))
                self.window.after(0, lambda s=fan_speed: self.update_analog_output("Ventilatora ātrums", s))
                
                # Atjaunina status
                self.memory["Sildīšanas režīms"] = False
                self.memory["Dzesēšanas režīms"] = True
                
                if self.cycle_count % 10 == 0:  # Lai neaizvērstu žurnālu
                    self.window.after(0, lambda: self.log_message(f"Dzesēšanas režīms, jauda: {cooler_power:.1f}%"))
            
            # Drošības ziņojumi, ja sistēma grib darboties, bet drošība to neļauj
            elif heating_mode and heater_safety_active and self.cycle_count % 20 == 0:
                self.window.after(0, lambda: self.log_message("⚠️ Sildīšana nepieciešama, bet bloķēta ar drošības releju!"))
                
            elif cooling_mode and cooler_safety_active and self.cycle_count % 20 == 0:
                self.window.after(0, lambda: self.log_message("⚠️ Dzesēšana nepieciešama, bet bloķēta ar drošības releju!"))
            
            else:
                # Sistēma uztur temperatūru (neaktīvs režīms)
                self.window.after(0, lambda: self.update_output("Sildītāja relejs", False))
                self.window.after(0, lambda: self.update_output("Dzesētāja relejs", False))
                
                # Izslēdz jaudas
                self.window.after(0, lambda: self.update_analog_output("Sildītāja jauda", 0))
                self.window.after(0, lambda: self.update_analog_output("Dzesētāja jauda", 0))
                
                # Minimālais ventilatora ātrums cirkulācijai
                self.window.after(0, lambda: self.update_analog_output("Ventilatora ātrums", 20))
                
                # Atjaunina status
                self.memory["Sildīšanas režīms"] = False
                self.memory["Dzesēšanas režīms"] = False
                
                if self.cycle_count % 20 == 0:  # Mazāk biežs ziņojums
                    self.window.after(0, lambda: self.log_message(f"Temperatūra stabilizēta: {current_temp:.1f}°C"))
            
            # Cikla aizture, lai nepārslogotu CPU
            time.sleep(0.5)
    
    def show(self):
        self.window.mainloop()


def open_plc_simulation():
    win = tk.Toplevel()
    win.title("PLC Simulācija")
    win.geometry("700x500")
    
    plc_sim = PLCSimulation(win)
    return plc_sim

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    plc_sim = PLCSimulation()
    plc_sim.show()
def open_plc_sim():
    win = tk.Toplevel()
    win.title("PLC simulācija")
    win.geometry("300x200")
    lbl = tk.Label(win, text="Simulācija notiek...", font=("Arial", 16))
    lbl.pack(pady=20)
    # Īslaicīga simulācija
    win.after(1000, lambda: lbl.config(text="Dati apstrādāti"))
    win.after(1000, lambda: print("PLC → Anomaly check done"))