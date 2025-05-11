import tkinter as tk
from tkinter import messagebox, ttk
import random
from model.predict import predict
import time
import math

class Process3Window:
    def __init__(self, master=None):
        if master is None:
            self.win = tk.Toplevel()
        else:
            self.win = master
            
        self.win.title("SCADA - Ventilācijas sistēmas process")
        self.win.geometry("800x600")
        self.win.minsize(700, 500)
        
        # Procesa stāvoklis
        self.running = False
        self.air_quality = 75.0  # Gaisa kvalitāte (%)
        self.target_quality = 95.0  # Mērķa gaisa kvalitāte (%)
        self.fan_speed = 50  # Ventilatora ātrums (%)
        self.filter_status = 100  # Filtra stāvoklis (%)
        self.humidity = 55  # Gaisa mitrums (%)
        
        # Krāsu definīcijas
        self.colors = {
            'bg': "#f5f5f5",
            'duct': "#d0d0d0",
            'fan_active': "#4CAF50",
            'fan_inactive': "#9e9e9e",
            'clean_air': "#a5d6ff",
            'dirty_air': "#b7a99e",
            'air_mixed': "#dce8f5",
            'filter': "#f0f0f0",
            'filter_dirty': "#c0c0c0",
            'panel_bg': "#e0e0e0",
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
        control_frame = ttk.LabelFrame(main_frame, text="Ventilācijas kontroles")
        control_frame.pack(fill=tk.X, pady=10)
        
        # Kontroles pogas un slaideri
        controls = ttk.Frame(control_frame)
        controls.pack(padx=20, pady=10)
        
        # Sākt/apturēt poga
        self.start_button = ttk.Button(controls, text="Sākt procesu", command=self.toggle_process)
        self.start_button.grid(row=0, column=0, padx=10, pady=5)
        
        # Ventilatora ātrums
        ttk.Label(controls, text="Ventilatora ātrums:").grid(row=0, column=1, padx=10, pady=5)
        self.speed_var = tk.StringVar(value=f"{self.fan_speed}%")
        ttk.Label(controls, textvariable=self.speed_var, width=8).grid(row=0, column=2, padx=5, pady=5)
        
        self.speed_slider = ttk.Scale(controls, from_=0, to=100, orient=tk.HORIZONTAL, 
                                     length=180, value=self.fan_speed,
                                     command=self.update_fan_speed)
        self.speed_slider.grid(row=0, column=3, padx=10, pady=5)
        
        # Filtra nomaiņas poga
        self.filter_button = ttk.Button(controls, text="Nomainīt filtru", command=self.replace_filter)
        self.filter_button.grid(row=0, column=4, padx=10, pady=5)
        
        # Canvas apgabals vizualizācijai
        self.canvas_frame = ttk.LabelFrame(main_frame, text="Ventilācijas sistēmas shēma")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg=self.colors['bg'])
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Informācijas panelis
        info_frame = ttk.LabelFrame(main_frame, text="Sistēmas informācija")
        info_frame.pack(fill=tk.X, pady=10)
        
        # Info paneļa saturs
        info_grid = ttk.Frame(info_frame)
        info_grid.pack(padx=20, pady=10)
        
        # Pirmā rinda - Gaisa kvalitāte un Mitrums
        ttk.Label(info_grid, text="Gaisa kvalitāte:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.quality_var = tk.StringVar(value=f"{self.air_quality:.1f}%")
        ttk.Label(info_grid, textvariable=self.quality_var, width=10).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(info_grid, text="Gaisa mitrums:", font=("Arial", 10, "bold")).grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.humidity_var = tk.StringVar(value=f"{self.humidity:.1f}%")
        ttk.Label(info_grid, textvariable=self.humidity_var, width=10).grid(row=0, column=3, sticky="w", padx=5, pady=2)
        
        # Otrā rinda - Filtra stāvoklis un Statuss
        ttk.Label(info_grid, text="Filtra stāvoklis:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.filter_var = tk.StringVar(value=f"{self.filter_status:.1f}%")
        ttk.Label(info_grid, textvariable=self.filter_var, width=10).grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
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
    
    def update_fan_speed(self, value):
        self.fan_speed = int(float(value))
        self.speed_var.set(f"{self.fan_speed}%")
    
    def replace_filter(self):
        """Nomaina filtru uz jaunu"""
        self.filter_status = 100.0
        self.filter_var.set(f"{self.filter_status:.1f}%")
        messagebox.showinfo("Filtrs nomainīts", "Ventilācijas filtrs ir veiksmīgi nomainīts!")
    
    def update_process(self):
        """Atjauno ventilācijas sistēmas stāvokli"""
        if self.running:
            # Filtra degradācijas aprēķins
            # Filtrs nodilst ātrāk, kad ventilators darbojas ar lielāku jaudu
            filter_degradation = (self.fan_speed / 100) * 0.05
            self.filter_status = max(0, self.filter_status - filter_degradation)
            
            # Gaisa kvalitātes aprēķins
            # Gaisa kvalitāte uzlabojas, kad ventilators darbojas
            # Bet efektivitāte samazinās, kad filtrs ir netīrs
            filter_efficiency = self.filter_status / 100
            quality_improvement = (self.fan_speed / 100) * 0.5 * filter_efficiency
            
            # Kvalitāte pasliktinās ar laiku (simulē gaisa piesārņojumu telpā)
            quality_degradation = 0.2
            
            # Kopējās izmaiņas gaisa kvalitātē
            self.air_quality = min(100, max(0, self.air_quality + quality_improvement - quality_degradation))
            
            # Gaisa mitruma aprēķins - nedaudz svārstās ap vidējo vērtību
            humidity_change = random.uniform(-0.5, 0.5)
            self.humidity = min(90, max(30, self.humidity + humidity_change))
            
            # Atjauninām informācijas paneļa vērtības
            self.quality_var.set(f"{self.air_quality:.1f}%")
            self.humidity_var.set(f"{self.humidity:.1f}%")
            self.filter_var.set(f"{self.filter_status:.1f}%")
            
            # Statusa atjaunināšana
            if self.filter_status < 20:
                self.status_var.set("NEPIECIEŠAMS FILTRS!")
            elif self.air_quality > 90:
                self.status_var.set("Teicama kvalitāte")
            elif self.air_quality > 70:
                self.status_var.set("Laba kvalitāte")
            elif self.air_quality > 50:
                self.status_var.set("Vidēja kvalitāte")
            else:
                self.status_var.set("Slikta kvalitāte")
        
        # Atjauninām vizualizāciju
        self.draw_process()
        
        # Ieplānojam nākamo atjauninājumu
        self.win.after(100, self.update_process)
    
    def draw_process(self):
        """Zīmē ventilācijas sistēmu ar animāciju"""
        # Notīrām canvas
        self.canvas.delete("all")
        
        # Iegūstam canvas izmērus
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width < 10 or height < 10:  # Canvas nav vēl inicializēts
            return
        
        # Aprēķinām elementu izmērus
        duct_width = width * 0.7
        duct_height = height * 0.2
        duct_x = width * 0.15
        duct_y = height * 0.3
        
        fan_radius = height * 0.1
        fan_x = duct_x + duct_width * 0.3
        fan_y = duct_y + duct_height / 2
        
        filter_width = width * 0.15
        filter_height = duct_height
        filter_x = duct_x + duct_width * 0.6
        filter_y = duct_y
        
        # Ventilācijas kanāla krāsas
        # Gaisa krāsa atkarībā no kvalitātes
        intake_color = self.blend_color(self.colors['dirty_air'], self.colors['clean_air'], self.air_quality / 100)
        
        # Galvenais ventilācijas kanāls
        self.canvas.create_rectangle(
            duct_x, duct_y, 
            duct_x + duct_width, duct_y + duct_height,
            fill=self.colors['duct'], outline="#555555", width=2
        )
        
        # Ieplūdes un izplūdes atveres
        # Ieplūdes atvere (kreisajā pusē)
        inlet_width = width * 0.1
        inlet_height = height * 0.3
        inlet_x = duct_x - inlet_width
        inlet_y = duct_y - inlet_height/3
        
        self.canvas.create_rectangle(
            inlet_x, inlet_y,
            duct_x, inlet_y + inlet_height,
            fill=self.colors['duct'], outline="#555555", width=2
        )
        
        # Izplūdes atvere (labajā pusē)
        outlet_width = width * 0.1
        outlet_height = height * 0.3
        outlet_x = duct_x + duct_width
        outlet_y = duct_y - outlet_height/3
        
        self.canvas.create_rectangle(
            outlet_x, outlet_y,
            outlet_x + outlet_width, outlet_y + outlet_height,
            fill=self.colors['duct'], outline="#555555", width=2
        )
        
        # Ventilācijas bultas, kas rāda gaisa plūsmu
        if self.running:
            # Ienākošais gaiss
            self.animate_air_flow(
                inlet_x, inlet_y + inlet_height/2,
                duct_x, duct_y + duct_height/2,
                intake_color, 8
            )
            
            # Gaiss pirms filtra
            pre_filter_color = intake_color
            self.animate_air_flow(
                fan_x + fan_radius, duct_y + duct_height/2,
                filter_x, duct_y + duct_height/2,
                pre_filter_color, 8, speed=0.8
            )
            
            # Izfiltrētais gaiss
            # Krāsa uzlabojas atkarībā no filtra efektivitātes
            filter_efficiency = self.filter_status / 100
            post_filter_color = self.blend_color(
                pre_filter_color, 
                self.colors['clean_air'],
                filter_efficiency
            )
            
            self.animate_air_flow(
                filter_x + filter_width, duct_y + duct_height/2,
                duct_x + duct_width, duct_y + duct_height/2,
                post_filter_color, 8, speed=0.8
            )
            
            # Izplūstošais gaiss
            self.animate_air_flow(
                outlet_x, outlet_y + outlet_height/2,
                outlet_x + outlet_width, outlet_y + outlet_height/2,
                post_filter_color, 8
            )
        
        # Ventilators
        fan_color = self.colors['fan_active'] if self.running else self.colors['fan_inactive']
        
        # Ventilatora korpuss
        self.canvas.create_oval(
            fan_x - fan_radius, fan_y - fan_radius,
            fan_x + fan_radius, fan_y + fan_radius,
            fill=fan_color, outline="#555555", width=2
        )
        
        # Ventilatora lāpstiņas
        if self.running:
            # Ventilatora rotācijas leņķis (atkarīgs no laika un ātruma)
            rotation = (time.time() * 5 * (self.fan_speed / 100)) % (2 * math.pi)
            
            # Lāpstiņu skaits
            blade_count = 6
            
            # Zīmējam lāpstiņas
            for i in range(blade_count):
                angle = rotation + i * (2 * math.pi / blade_count)
                
                # Lāpstiņas koordinātas
                blade_length = fan_radius * 0.7
                end_x = fan_x + math.cos(angle) * blade_length
                end_y = fan_y + math.sin(angle) * blade_length
                
                # Lāpstiņas platums
                blade_width = 4
                
                self.canvas.create_line(
                    fan_x, fan_y, end_x, end_y,
                    fill="white", width=blade_width, 
                    capstyle="round"
                )
        
        # Ventilatora ātrums tekstā
        if self.running:
            self.canvas.create_text(
                fan_x, fan_y,
                text=f"{self.fan_speed}%",
                font=("Arial", 9, "bold"),
                fill="white"
            )
        else:
            self.canvas.create_text(
                fan_x, fan_y,
                text="OFF",
                font=("Arial", 10, "bold"),
                fill="white"
            )
        
        # Filtrs
        # Filtra krāsa mainās atkarībā no tā stāvokļa
        filter_dirt_ratio = 1 - (self.filter_status / 100)
        filter_color = self.blend_color(
            self.colors['filter'], 
            self.colors['filter_dirty'],
            filter_dirt_ratio
        )
        
        self.canvas.create_rectangle(
            filter_x, filter_y,
            filter_x + filter_width, filter_y + filter_height,
            fill=filter_color, outline="#555555", width=2
        )
        
        # Filtra iekšējās līnijas
        line_count = 5
        line_spacing = filter_height / (line_count + 1)
        
        for i in range(1, line_count + 1):
            line_y = filter_y + i * line_spacing
            self.canvas.create_line(
                filter_x, line_y,
                filter_x + filter_width, line_y,
                fill="#777777", dash=(3, 2)
            )
        
        # Filtrs teksts
        self.canvas.create_text(
            filter_x + filter_width/2, filter_y + filter_height/2,
            text=f"Filtrs\n{self.filter_status:.0f}%",
            font=("Arial", 9, "bold"),
            fill="#333333"
        )
        
        # Gaisa kvalitātes rādītājs kreisajā pusē
        self.draw_quality_indicator(inlet_x/2, height * 0.7, width * 0.06, self.air_quality, "Gaisa kvalitāte")
        
        # Mitruma rādītājs labajā pusē
        self.draw_quality_indicator(width - inlet_x/2, height * 0.7, width * 0.06, self.humidity, "Mitrums")
    
    def draw_quality_indicator(self, x, y, radius, value, label):
        """Zīmē apaļu rādītāju ar vērtību"""
        # Fona aplis
        self.canvas.create_oval(
            x - radius, y - radius,
            x + radius, y + radius,
            fill="white", outline="#555555", width=2
        )
        
        # Krāsu gradients atkarībā no vērtības
        if value > 80:
            color = "#4CAF50"  # Zaļš - labs
        elif value > 60:
            color = "#8BC34A"  # Gaiši zaļš - OK
        elif value > 40:
            color = "#FFC107"  # Dzeltens - viduvējs
        elif value > 20:
            color = "#FF9800"  # Oranžs - slikts
        else:
            color = "#F44336"  # Sarkans - kritisks
        
        # Sektors, kas rāda vērtību
        # Aprēķinām leņķi (90 grādi ir augšā, grādi pieaug pulksteņrādītāja virzienā)
        angle = 90 - (value / 100 * 360)
        
        # Zīmējam sektoru
        self.canvas.create_arc(
            x - radius, y - radius,
            x + radius, y + radius,
            start=90, extent=-value / 100 * 360,
            fill=color, outline=color
        )
        
        # Centrālais mazais aplis
        inner_radius = radius * 0.7
        self.canvas.create_oval(
            x - inner_radius, y - inner_radius,
            x + inner_radius, y + inner_radius,
            fill="white", outline=color, width=2
        )
        
        # Vērtība
        self.canvas.create_text(
            x, y,
            text=f"{value:.0f}%",
            font=("Arial", 10, "bold"),
            fill="#333333"
        )
        
        # Nosaukums zem rādītāja
        self.canvas.create_text(
            x, y + radius + 15,
            text=label,
            font=("Arial", 9),
            fill="#333333"
        )
    
    def animate_air_flow(self, x1, y1, x2, y2, color, width, vertical=False, speed=1.0):
        """Animē gaisa plūsmu ar bultu punktu sēriju"""
        # Aprēķinām kanāla garumu
        length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        
        # Cik daudz bultu zīmēt
        num_points = int(length / 30)
        
        # Laika fāze animācijai (0-1) ar ātruma kontroli
        phase = (time.time() * 2 * speed) % 1.0
        
        # Vektora vienības virziens
        dx = (x2 - x1) / length
        dy = (y2 - y1) / length
        
        for i in range(num_points):
            # Punkta pozīcija (0-1)
            pos = (i / num_points + phase) % 1.0
            
            # Aprēķinam punkta koordinātes
            px = x1 + (x2 - x1) * pos
            py = y1 + (y2 - y1) * pos
            
            # Bultas lielums (atkarīgs no ventilatora ātruma)
            arrow_size = width * 0.8 * (0.5 + self.fan_speed / 200)
            
            # Zīmējam bultu (trijstūri) plūsmas virzienā
            self.canvas.create_polygon(
                px, py,
                px - arrow_size * dx + arrow_size * dy * 0.5, py - arrow_size * dy - arrow_size * dx * 0.5,
                px - arrow_size * dx - arrow_size * dy * 0.5, py - arrow_size * dy + arrow_size * dx * 0.5,
                fill=color, outline=""
            )
    
    def blend_color(self, color1, color2, ratio):
        """Sajauc divas krāsas ar noteiktu attiecību (0-1)"""
        # Pārvēršam hex krāsas RGB vērtībās
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        
        # Lineāri interpolējam krāsu komponentes
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        
        # Atgriežam hex formātā
        return f"#{r:02x}{g:02x}{b:02x}"
        
def open_process3():
    """Atver Process 3 logu"""
    return Process3Window()

def show_simple_process3():
    """Atver vienkāršotu Process 3 logu"""
    win = tk.Toplevel()
    win.title("Process 3 - Ventilācijas sistēma")
    win.geometry("350x280")
    
    # Header
    tk.Label(win, text="Ventilācijas sistēmas monitorings", 
             font=("Arial", 14, "bold")).pack(pady=10)
    
    # Add frame for sensor readings
    readings_frame = ttk.LabelFrame(win, text="Sensoru rādījumi")
    readings_frame.pack(fill="both", expand=True, padx=15, pady=5)
    
    try:
        # Create data values for ventilation system
        data = {
            'temp': random.uniform(20, 22),
            'pressure': random.uniform(1.0, 1.03),
            'flow': random.uniform(80, 95)
        }
            
        # Get prediction from model
        pred = predict(data)
        
        # Normal operating ranges (for display)
        normal_ranges = {
            'temp': "20°C - 22°C",
            'pressure': "1.0 - 1.03 bar",
            'flow': "80 - 95 l/min"
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
                is_normal = 20 <= data['temp'] <= 22
            elif param == "Spiediens":
                is_normal = 1.0 <= data['pressure'] <= 1.03
            else:  # Flow
                is_normal = 80 <= data['flow'] <= 95
                
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
        
        # Display status based on model prediction
        if pred == "FAULT":
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
    show_simple_process3()
