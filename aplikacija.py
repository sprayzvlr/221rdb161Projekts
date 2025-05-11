from model.train import train
from scada_gui.main_window import run_main_window
import os

if __name__ == '__main__':
    # Ja modelis nav apmācīts, trenē
    if not os.path.exists('model/model.pkl'):
        print("Model not found. Training model...")
        train()
    else:
        print("Model already exists. Skipping training.")

    # Startē GUI
    run_main_window()