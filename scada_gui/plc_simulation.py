import tkinter as tk
import time
from model.predict import predict

def open_plc_sim():
    win = tk.Toplevel()
    win.title("PLC simulācija")
    win.geometry("300x200")
    lbl = tk.Label(win, text="Simulācija notiek...", font=("Arial", 16))
    lbl.pack(pady=20)
    # Īslaicīga simulācija
    win.after(1000, lambda: lbl.config(text="Dati apstrādāti"))
    win.after(1000, lambda: print("PLC → Anomaly check done"))