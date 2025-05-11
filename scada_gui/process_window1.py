import tkinter as tk
from tkinter import messagebox, ttk
import random
from model.predict import predict
import tkinter as tk
from tkinter import ttk
import time
import random
import math
from PIL import Image, ImageTk, ImageDraw
import io

class Process1Window:
    def __init__(self, master=None):
        if master is None:
            self.win = tk.Toplevel()
        else:
            self.win = master
            
        self.win.title("SCADA - Sildīšanas sistēmas process")
        self.win.geometry("900x700")
        self.win.minsize(800, 600)
        
        # Procesa stāvoklis
        self.running = False
        self.temperature = 20.0  # Sākuma temperatūra
        self.target_temp = 70.0  # Mērķa temperatūra
        self.heater_power = 50   # Sildītāja jauda (%)
        self.flow_rate = 2.0     # Plūsmas ātrums (l/min)
        self.valve_position = 50 # Vārsta pozīcija (%)
        
        # Krāsu definīcijas
        self.colors = {
            'bg': "#f0f0f0",
            'pipe': "#c0c0c0",
            'hot_fluid': "#ff6b6b",
            'cold_fluid': "#5da4e4",
            'warm_fluid': "#ffa86b",
            'tank': "#d0d0d0",
            'heater': "#e74c3c",
            'panel_bg': "#e0e0e0",
            'active': "#4CAF50",
            'inactive': "#9e9e9e",
            'warning': "#FFC107",
            'text': "#333333",
        }
        
        # Uzstādam lietotāja saskarni
        self.setup_ui()
        
        # Sākam animāciju
        self.update_process()
    
    def setup_ui(self):
        # Galvenais rāmis
        main_frame = ttk.Frame(self.win)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Augšējais rāmis ar kontrolēm
        control_frame = ttk.LabelFrame(main_frame, text="Sistēmas kontroles")
        control_frame.pack(fill=tk.X, pady=10)
        
        # Kontroles pogas un slaideri
        controls_left = ttk.Frame(control_frame)
        controls_left.pack(side=tk.LEFT, padx=20, pady=10)
        
        controls_right = ttk.Frame(control_frame)
        controls_right.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Kreisā puse - pogas
        self.start_button = ttk.Button(controls_left, text="Sākt procesu", command=self.toggle_process)
        self.start_button.pack(pady=5)
        
        # Mērķa temperatūra
        temp_frame = ttk.Frame(controls_left)
        temp_frame.pack(pady=5, fill=tk.X)
        
        ttk.Label(temp_frame, text="Mērķa temperatūra:").pack(side=tk.LEFT, padx=5)
        self.temp_var = tk.StringVar(value=f"{self.target_temp} °C")
        ttk.Label(temp_frame, textvariable=self.temp_var, width=8).pack(side=tk.LEFT, padx=5)
        
        # Temperatūras slīdnis
        self.temp_slider = ttk.Scale(controls_left, from_=20, to=100, orient=tk.HORIZONTAL, 
                                     length=180, value=self.target_temp,
                                     command=self.update_target_temp)
        self.temp_slider.pack(pady=5)
        
        # Labā puse - slaideri
        # Sildītāja jauda
        power_frame = ttk.Frame(controls_right)
        power_frame.pack(pady=5, fill=tk.X)
        
        ttk.Label(power_frame, text="Sildītāja jauda:").pack(side=tk.LEFT, padx=5)
        self.power_var = tk.StringVar(value=f"{self.heater_power}%")
        ttk.Label(power_frame, textvariable=self.power_var, width=8).pack(side=tk.LEFT, padx=5)
        
        self.power_slider = ttk.Scale(controls_right, from_=0, to=100, orient=tk.HORIZONTAL, 
                                     length=180, value=self.heater_power,
                                     command=self.update_heater_power)
        self.power_slider.pack(pady=5)
        
        # Vārsta pozīcija
        valve_frame = ttk.Frame(controls_right)
        valve_frame.pack(pady=5, fill=tk.X)
        
        ttk.Label(valve_frame, text="Vārsta pozīcija:").pack(side=tk.LEFT, padx=5)
        self.valve_var = tk.StringVar(value=f"{self.valve_position}%")
        ttk.Label(valve_frame, textvariable=self.valve_var, width=8).pack(side=tk.LEFT, padx=5)
        
        self.valve_slider = ttk.Scale(controls_right, from_=0, to=100, orient=tk.HORIZONTAL, 
                                    length=180, value=self.valve_position,
                                    command=self.update_valve_position)
        self.valve_slider.pack(pady=5)
        
        # Canvas apgabals vizualizācijai
        self.canvas_frame = ttk.LabelFrame(main_frame, text="Sildīšanas sistēmas shēma")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg=self.colors['bg'])
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Informācijas panelis
        info_frame = ttk.LabelFrame(main_frame, text="Sistēmas informācija")
        info_frame.pack(fill=tk.X, pady=10)
        
        # Info paneļa saturs
        info_grid = ttk.Frame(info_frame)
        info_grid.pack(padx=20, pady=10)
        
        # Pirmā rinda - Temperatūra un Plūsma
        ttk.Label(info_grid, text="Pašreizējā temperatūra:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.current_temp_var = tk.StringVar(value=f"{self.temperature:.1f} °C")
        ttk.Label(info_grid, textvariable=self.current_temp_var, width=10).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(info_grid, text="Plūsmas ātrums:", font=("Arial", 10, "bold")).grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.flow_var = tk.StringVar(value=f"{self.flow_rate:.1f} l/min")
        ttk.Label(info_grid, textvariable=self.flow_var, width=10).grid(row=0, column=3, sticky="w", padx=5, pady=2)
        
        # Otrā rinda - Efektivitāte un statuss
        ttk.Label(info_grid, text="Sildīšanas efektivitāte:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.efficiency_var = tk.StringVar(value="0%")
        ttk.Label(info_grid, textvariable=self.efficiency_var, width=10).grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(info_grid, text="Sistēmas statuss:", font=("Arial", 10, "bold")).grid(row=1, column=2, sticky="w", padx=5, pady=2)
        self.status_var = tk.StringVar(value="Gaidstāve")
        ttk.Label(info_grid, textvariable=self.status_var, width=15).grid(row=1, column=3, sticky="w", padx=5, pady=2)
    
    def toggle_process(self):
        self.running = not self.running
        
        if self.running:
            self.start_button.config(text="Apturēt procesu")
            self.status_var.set("Darbojas")
        else:
            self.start_button.config(text="Sākt procesu")
            self.status_var.set("Gaidstāve")
    
    def update_target_temp(self, value):
        self.target_temp = float(value)
        self.temp_var.set(f"{int(self.target_temp)} °C")
    
    def update_heater_power(self, value):
        self.heater_power = int(float(value))
        self.power_var.set(f"{self.heater_power}%")
    
    def update_valve_position(self, value):
        self.valve_position = int(float(value))
        self.valve_var.set(f"{self.valve_position}%")
    
    def update_process(self):
        # Atjauninām procesa stāvokli
        if self.running:
            # Aprēķinām jauno temperatūru
            temp_diff = self.target_temp - self.temperature
            
            # Temperatūras izmaiņas ātrums atkarīgs no sildītāja jaudas un vārsta pozīcijas
            heat_factor = (self.heater_power / 100) * 0.2  # Max 0.2 grādi par takti
            cooling_factor = 0.05 * (1 - self.valve_position / 100)  # Dzesēšanas efekts
            
            # Pievienojam nejaušības faktoru
            random_factor = random.uniform(-0.05, 0.05)
            
            if temp_diff > 0:
                # Sildām
                self.temperature += heat_factor - cooling_factor + random_factor
            else:
                # Dzesējam (lēnāk)
                self.temperature += -0.05 - cooling_factor + random_factor
            
            # Ierobežojam temperatūru
            self.temperature = max(18, min(self.temperature, 105))
            
            # Atjauninām plūsmas ātrumu
            flow_base = 1.0 + (self.valve_position / 100) * 3.0  # 1-4 l/min
            self.flow_rate = flow_base + random.uniform(-0.1, 0.1)
            
            # Aprēķinām efektivitāti
            efficiency = max(0, min(100, (self.temperature / self.target_temp) * 100))
            if self.temperature > self.target_temp + 10:
                efficiency = 50  # Pārkaršana samazina efektivitāti
            
            # Atjauninām informācijas paneļa vērtības
            self.current_temp_var.set(f"{self.temperature:.1f} °C")
            self.flow_var.set(f"{self.flow_rate:.1f} l/min")
            self.efficiency_var.set(f"{int(efficiency)}%")
            
            # Atjauninām sistēmas statusu
            if abs(self.temperature - self.target_temp) < 3:
                self.status_var.set("Optimāls")
            elif self.temperature < self.target_temp:
                self.status_var.set("Sildīšana")
            elif self.temperature > self.target_temp + 10:
                self.status_var.set("Pārkaršana!")
            else:
                self.status_var.set("Dzesēšana")
        
        # Atjauninām vizualizāciju
        self.draw_process()
        
        # Ieplānojam nākamo atjauninājumu
        self.win.after(100, self.update_process)
    
    def draw_process(self):
        """Zīmē sildīšanas sistēmas shēmu ar animāciju"""
        # Notīrām canvas
        self.canvas.delete("all")
        
        # Iegūstam canvas izmērus
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width < 10 or height < 10:  # Canvas nav vēl inicializēts
            return
        
        # Aprēķinām elementu izmērus
        tank_width = width * 0.15
        tank_height = height * 0.5
        tank_x = width * 0.15
        tank_y = height * 0.25
        
        heater_width = width * 0.15
        heater_height = height * 0.2
        heater_x = width * 0.5
        heater_y = height * 0.4
        
        pipe_width = 15
        
        # Aprēķinām krāsu temperatūrai
        temp_ratio = min(1.0, max(0, (self.temperature - 20) / 80))
        r = int(93 + temp_ratio * 162)
        g = int(164 - temp_ratio * 100)
        b = int(228 - temp_ratio * 163)
        fluid_color = f"#{r:02x}{g:02x}{b:02x}"
        
        # --- Zīmējam cauruļvadu sistēmu ---
        
        # Galvenā tvertne
        self.canvas.create_rectangle(tank_x, tank_y, tank_x + tank_width, tank_y + tank_height, 
                                    fill=self.colors['tank'], outline="#555555", width=2)
        
        # Ūdens līmenis tvertnē
        water_level = 0.9  # 90% pilna
        water_height = tank_height * water_level
        water_y = tank_y + (tank_height - water_height)
        
        self.canvas.create_rectangle(tank_x, water_y, tank_x + tank_width, tank_y + tank_height, 
                                    fill=fluid_color, outline="")
        
        # Temperatūra uz tvertnes
        self.canvas.create_text(tank_x + tank_width/2, tank_y + tank_height + 20, 
                               text=f"{self.temperature:.1f}°C", 
                               font=("Arial", 10, "bold"), fill=self.colors['text'])
        
        # Sildītājs
        heater_color = self.colors['heater'] if self.running and self.heater_power > 0 else "#888888"
        self.canvas.create_rectangle(heater_x, heater_y, heater_x + heater_width, heater_y + heater_height, 
                                    fill=heater_color, outline="#555555", width=2)
        
        # Sildītāja teksts
        self.canvas.create_text(heater_x + heater_width/2, heater_y + heater_height/2, 
                               text=f"Sildītājs\n{self.heater_power}%", 
                               font=("Arial", 10, "bold"), fill="white")
        
        # --- Cauruļvadi ---
        
        # 1. Izplūdes caurule no tvertnes
        pipe1_x1 = tank_x + tank_width
        pipe1_y1 = tank_y + tank_height * 0.7
        pipe1_x2 = heater_x
        pipe1_y2 = pipe1_y1
        
        self.canvas.create_line(pipe1_x1, pipe1_y1, pipe1_x2, pipe1_y2, 
                              fill=self.colors['pipe'], width=pipe_width, capstyle="round")
        
        # Plūsma caurulē 1
        if self.running:
            self.animate_flow(pipe1_x1, pipe1_y1, pipe1_x2, pipe1_y2, fluid_color, pipe_width-4)
        
        # 2. Caurule no sildītāja uz atgriešanās līniju
        pipe2_x1 = heater_x + heater_width
        pipe2_y1 = heater_y + heater_height/2
        pipe2_x2 = width * 0.75
        pipe2_y2 = pipe2_y1
        
        self.canvas.create_line(pipe2_x1, pipe2_y1, pipe2_x2, pipe2_y2, 
                              fill=self.colors['pipe'], width=pipe_width, capstyle="round")
        
        # Plūsma caurulē 2
        if self.running:
            # Šeit šķidrums ir karstāks
            hotter_fluid = self.colors['hot_fluid']
            self.animate_flow(pipe2_x1, pipe2_y1, pipe2_x2, pipe2_y2, hotter_fluid, pipe_width-4)
        
        # 3. Vertikālā atgriešanās caurule
        pipe3_x1 = pipe2_x2
        pipe3_y1 = pipe2_y2
        pipe3_x2 = pipe3_x1
        pipe3_y2 = tank_y + tank_height * 0.3
        
        self.canvas.create_line(pipe3_x1, pipe3_y1, pipe3_x2, pipe3_y2, 
                              fill=self.colors['pipe'], width=pipe_width, capstyle="round")
        
        # Plūsma caurulē 3
        if self.running:
            self.animate_flow(pipe3_x1, pipe3_y1, pipe3_x2, pipe3_y2, fluid_color, pipe_width-4, vertical=True)
        
        # 4. Atgriešanās caurule uz tvertni
        pipe4_x1 = pipe3_x2
        pipe4_y1 = pipe3_y2
        pipe4_x2 = tank_x + tank_width
        pipe4_y2 = pipe4_y1
        
        self.canvas.create_line(pipe4_x1, pipe4_y1, pipe4_x2, pipe4_y2, 
                              fill=self.colors['pipe'], width=pipe_width, capstyle="round")
        
        # Plūsma caurulē 4
        if self.running:
            self.animate_flow(pipe4_x1, pipe4_y1, pipe4_x2, pipe4_y2, fluid_color, pipe_width-4, reverse=True)
        
        # --- Vārsti un sensori ---
        
        # Vārsts uz izplūdes caurules
        valve_x = pipe1_x1 + (pipe1_x2 - pipe1_x1) * 0.3
        valve_y = pipe1_y1
        valve_size = pipe_width * 1.5
        
        # Vārsta korpuss
        self.canvas.create_oval(valve_x - valve_size/2, valve_y - valve_size/2,
                              valve_x + valve_size/2, valve_y + valve_size/2,
                              fill="#888888", outline="#555555", width=2)
        
        # Vārsta rokturis - rotējas atkarībā no pozīcijas
        valve_angle = (self.valve_position / 100) * 90
        valve_handle_length = valve_size * 0.7
        valve_handle_x = valve_x + math.cos(math.radians(valve_angle)) * valve_handle_length
        valve_handle_y = valve_y - math.sin(math.radians(valve_angle)) * valve_handle_length
        
        self.canvas.create_line(valve_x, valve_y, valve_handle_x, valve_handle_y,
                              fill="#333333", width=3, capstyle="round")
        
        # Vārsta teksts
        self.canvas.create_text(valve_x, valve_y + valve_size, 
                             text=f"Vārsts {self.valve_position}%", 
                             font=("Arial", 9), fill=self.colors['text'])
        
        # Temperatūras sensors uz atgriešanās caurules
        sensor_x = pipe4_x1 - (pipe4_x1 - pipe4_x2) * 0.3
        sensor_y = pipe4_y1
        sensor_size = pipe_width * 1.2
        
        sensor_color = "#4CAF50" if abs(self.temperature - self.target_temp) < 5 else "#FFC107"
        if self.temperature > self.target_temp + 10:
            sensor_color = "#F44336"
        
        self.canvas.create_rectangle(sensor_x - sensor_size/2, sensor_y - sensor_size/2,
                                   sensor_x + sensor_size/2, sensor_y + sensor_size/2, 
                                   fill=sensor_color, outline="#555555", width=2)
        
        self.canvas.create_text(sensor_x, sensor_y, 
                              text="T", font=("Arial", 10, "bold"), fill="white")
        
        self.canvas.create_text(sensor_x, sensor_y + sensor_size, 
                             text=f"{self.temperature:.1f}°C", 
                             font=("Arial", 9), fill=self.colors['text'])
    
    def animate_flow(self, x1, y1, x2, y2, color, width, vertical=False, reverse=False, speed=1.0):
        """Animē plūsmu caurulē, izmantojot punktu sēriju"""
        # Aprēķinām cauruļvada garumu
        if vertical:
            length = abs(y2 - y1)
        else:
            length = abs(x2 - x1)
        
        # Cik daudz punktu zīmēt
        num_points = int(length / 15)
        
        # Laika fāze animācijai (0-1) ar ātruma kontroli
        phase = (time.time() * 2 * speed) % 1.0
        
        # Ja reverse, tad apgriežam plūsmas virzienu
        if reverse:
            phase = 1.0 - phase
        
        for i in range(num_points):
            # Punkta pozīcija (0-1)
            pos = (i / num_points + phase) % 1.0
            
            # Aprēķinam punkta koordinātes
            if vertical:
                px = x1
                py = y1 + (y2 - y1) * pos
            else:
                px = x1 + (x2 - x1) * pos
                py = y1
            
            # Zīmējam punktu
            dot_size = width * 0.8
            self.canvas.create_oval(px - dot_size/2, py - dot_size/2,
                                  px + dot_size/2, py + dot_size/2,
                                  fill=color, outline="")

def open_process1():
    """Atver Process 1 logu"""
    return Process1Window()

def show_simple_process1():
    win = tk.Toplevel()
    win.title("Process 1 - Sildīšanas sistēma")
    win.geometry("350x280")
    
    # Header
    tk.Label(win, text="Sildīšanas sistēmas monitorings", 
             font=("Arial", 14, "bold")).pack(pady=10)
    
    # Add frame for sensor readings
    readings_frame = ttk.LabelFrame(win, text="Sensoru rādījumi")
    readings_frame.pack(fill="both", expand=True, padx=15, pady=5)
    
    try:
        # Generate data with chance of showing anomaly
        show_anomaly = random.random() > 0.7  # 30% chance of showing anomaly
        
        if show_anomaly:
            # Generate abnormal data
            anomaly_type = random.choice(['temp', 'pressure', 'flow'])
            
            data = {
                'temp': random.uniform(26, 30) if anomaly_type == 'temp' else random.uniform(21.5, 23.8),
                'pressure': random.uniform(1.15, 1.2) if anomaly_type == 'pressure' else random.uniform(1.01, 1.05),
                'flow': random.uniform(70, 85) if anomaly_type == 'flow' else random.uniform(97, 103)
            }
        else:
            # Normal operating ranges
            data = {
                'temp': random.uniform(21.5, 23.8),
                'pressure': random.uniform(1.01, 1.05),
                'flow': random.uniform(97, 103)
            }
        
        # Get prediction from model (but we'll override it for demo purposes)
        pred = predict(data)
        
        # Debug print to see what model predicts
        print(f"Process 1 - Generated data: {data}, Prediction: {pred}")
        
        # Normal operating ranges (for display)
        normal_ranges = {
            'temp': "21.5°C - 23.8°C",
            'pressure': "1.01 - 1.05 bar",
            'flow': "97 - 103 l/min"
        }
        
        # Display sensor readings with units and normal ranges
        readings = [
            ("Temperatūra", f"{data['temp']:.1f}°C", normal_ranges['temp']),
            ("Spiediens", f"{data['pressure']:.2f} bar", normal_ranges['pressure']),
            ("Plūsma", f"{data['flow']:.0f} l/min", normal_ranges['flow'])
        ]
        
        # Create display grid
        ttk.Label(readings_frame, text="Parametrs", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(readings_frame, text="Vērtība", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(readings_frame, text="Norma", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        
        for i, (param, value, normal) in enumerate(readings, 1):
            ttk.Label(readings_frame, text=param).grid(row=i, column=0, padx=5, pady=3, sticky="w")
            
            # Color the value based on whether it's in normal range
            is_normal = False
            if param == "Temperatūra":
                is_normal = 21.5 <= data['temp'] <= 23.8
            elif param == "Spiediens":
                is_normal = 1.01 <= data['pressure'] <= 1.05
            else:  # Flow
                is_normal = 97 <= data['flow'] <= 103
                
            value_label = ttk.Label(readings_frame, text=value)
            value_label.grid(row=i, column=1, padx=5, pady=3, sticky="w")
            if not is_normal:
                value_label.configure(foreground="red")
                
            ttk.Label(readings_frame, text=normal).grid(row=i, column=2, padx=5, pady=3, sticky="w")
        
        # Status section
        status_frame = ttk.Frame(win)
        status_frame.pack(fill="x", padx=15, pady=10)
        
        status_label = ttk.Label(status_frame, text="Sistēmas statuss:", font=("Arial", 10, "bold"))
        status_label.pack(side="left", padx=(0, 5))
        
        # For demo purposes: Show anomaly based on whether any value is outside normal range
        any_abnormal = (
            data['temp'] < 21.5 or data['temp'] > 23.8 or
            data['pressure'] < 1.01 or data['pressure'] > 1.05 or
            data['flow'] < 97 or data['flow'] > 103
        )
        
        if any_abnormal:
            result_label = ttk.Label(status_frame, text="ANOMĀLIJA", foreground="red", font=("Arial", 10, "bold"))
        else:
            result_label = ttk.Label(status_frame, text="NORMĀLS", foreground="green", font=("Arial", 10, "bold"))
        result_label.pack(side="left")
        
        # Refresh button
        refresh_btn = ttk.Button(win, text="Atjaunot datus", command=lambda: refresh_data(win))
        refresh_btn.pack(pady=10)

    except FileNotFoundError:
        messagebox.showerror(
            "Kļūda",
            "Modelis nav atrasts. Lūdzu, apmāciet modeli vispirms."
        )
        win.destroy()
    except Exception as e:
        messagebox.showerror("Kļūda", f"Radās kļūda: {str(e)}")
        win.destroy()

def refresh_data(win):
    win.destroy()
    show_simple_process1()
