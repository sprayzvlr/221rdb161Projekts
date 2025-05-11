import tkinter as tk
from scada_gui.statistics_window import open_statistics
from scada_gui.process_window1 import open_process1
from scada_gui.process_window2 import open_process2
from scada_gui.process_window3 import open_process3
from scada_gui.plc_simulation import open_plc_simulation as open_plc_sim

# vizuālie efekti
def apply_hover_effects(button, normal_bg, hover_bg):
    def on_enter(event):
        button.config(bg=hover_bg)
    def on_leave(event):
        button.config(bg=normal_bg)
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)

def run_main_window():
    root = tk.Tk()
    root.title("Autors - Linards Tomass Bekeris")
    root.geometry("700x800")
    root.config(bg="#333333")

    # === Virsraksts (ar ēnu) ===
    header_container = tk.Frame(root, bg="#333333")
    header_container.pack(pady=30)

    # Ēna
    shadow = tk.Label(header_container, text="Studiju projekta galvenais logs",
                      font=("Helvetica", 28, "bold"),
                      bg="#333333", fg="#111111")
    shadow.place(x=3, y=3)

    # Virsraksts ar card dizainu
    header_frame = tk.Frame(header_container, bg="#444444", bd=2, relief="groove")
    header_frame.pack()

    header = tk.Label(header_frame, text="Studiju projekta galvenais logs",
                      font=("Helvetica", 28, "bold"),
                      bg="#444444", fg="#ffffff", padx=10, pady=10)
    header.pack()

    # Pogu dizains
    button_style = {
        'width': 20,
        'height': 3,
        'font': ("Arial", 16, "bold"),
        'bg': "#555555",
        'fg': "#f0f0f0",
        'bd': 3,
        'relief': "solid",
        'activebackground': "#666666",
        'activeforeground': "#ffffff",
        'highlightbackground': "#555555",
        'highlightthickness': 2,
        'padx': 20,
        'pady': 10,
        'borderwidth': 0,
        'overrelief': "sunken",
    }

    # Pogas
    buttons = [
        ("Statistika", open_statistics),
        ("Process 1", open_process1),
        ("Process 2", open_process2),
        ("Process 3", open_process3),
        ("PLC Simulācija", open_plc_sim)
    ]

    for text, command in buttons:
        btn = tk.Button(root, text=text, command=command, **button_style)
        btn.pack(pady=10)
        apply_hover_effects(btn, normal_bg="#555555", hover_bg="#777777")

    root.mainloop()
