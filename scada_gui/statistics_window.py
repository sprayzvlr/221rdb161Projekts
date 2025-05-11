import tkinter as tk
from model.evaluate import evaluate

def open_statistics():
    win = tk.Toplevel()
    win.title("SCADA AI – Statistika")
    win.geometry("400x300")
    tk.Label(win, text="Statistikas logs", font=("Arial", 18, "bold")).pack(pady=10)
    # Izsauc apmācītā modeļa novērtējumu konsolē
    evaluate()
    tk.Label(win, text="Skati konsoli precīzākiem rezultātiem").pack(pady=20)