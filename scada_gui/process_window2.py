import tkinter as tk
import random
from model.predict import predict

def open_process2():
    win = tk.Toplevel()
    win.title("Process 2")
    win.geometry("300x200")
    tk.Label(win, text="Process 2 dati", font=("Arial", 16)).pack(pady=10)
    data = {'temp': random.uniform(25,30),
            'pressure': random.uniform(1.1,1.2),
            'flow': random.uniform(80,90)}
    pred = predict(data)
    tk.Label(win, text=f"Temp: {data['temp']:.1f}").pack()
    tk.Label(win, text=f"Pressure: {data['pressure']:.2f}").pack()
    tk.Label(win, text=f"Flow: {data['flow']:.0f}").pack()
    tk.Label(win, text=f"Anomaly: {pred}", fg="red" if pred else "green").pack(pady=10)