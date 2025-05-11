import tkinter as tk
from tkinter import messagebox, ttk
import random
from model.predict import predict


def open_process1():
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
    open_process1()
