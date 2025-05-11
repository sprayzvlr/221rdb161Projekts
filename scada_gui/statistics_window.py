import tkinter as tk
from tkinter import ttk
from model.evaluate import evaluate
import numpy as np

def open_statistics():
    win = tk.Toplevel()
    win.title("SCADA AI – Statistika")
    win.geometry("600x400")
    win.minsize(600, 400)

    def show_error(message):
        error_label = tk.Label(win, text=message,
                             fg="red",
                             wraplength=550)
        error_label.pack(pady=20)

    tk.Label(win, text="Modeļa statistikas rezultāti",
            font=("Arial", 18, "bold")).pack(pady=10)

    # Create a frame for the statistics
    stats_frame = ttk.Frame(win, padding="10")
    stats_frame.pack(fill=tk.BOTH, expand=True)

    try:
        # Get evaluation metrics
        results = evaluate()
        
        if results:
            # Display accuracy
            accuracy_frame = ttk.LabelFrame(stats_frame, text="Precizitāte")
            accuracy_frame.pack(fill=tk.X, pady=5)
            
            accuracy_val = results['accuracy'] * 100
            accuracy_label = tk.Label(
                accuracy_frame, 
                text=f"{accuracy_val:.1f}%", 
                font=("Arial", 24, "bold"),
                fg="green" if accuracy_val > 80 else "orange" if accuracy_val > 70 else "red"
            )
            accuracy_label.pack(pady=5)
            
            # Sample size info
            sample_label = tk.Label(
                accuracy_frame,
                text=f"Balstīts uz {results['test_size']} testa paraugiem",
                font=("Arial", 10)
            )
            sample_label.pack()
            
            # Instructions for more details
            tk.Label(
                win,
                text="Detalizēts modeļa novērtējums ir pieejams terminālī",
                font=("Arial", 10, "italic")
            ).pack(pady=10)
            
            # Add button to close window
            close_button = ttk.Button(win, text="Aizvērt", command=win.destroy)
            close_button.pack(pady=10)
        else:
            show_error("Neizdevās iegūt statistikas datus")
            
    except FileNotFoundError as e:
        show_error(f"Kļūda: Nav atrasts modelis vai skalers.\n"
                  f"Lūdzu pārliecinieties, ka modelis ir apmācīts.\n{str(e)}")
    except Exception as e:
        show_error(f"Kļūda aprēķinot statistiku: {str(e)}")