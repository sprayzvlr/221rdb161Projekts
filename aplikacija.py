from model.train import train
from scada_gui.main_window import run_main_window
import os
from model.train import train
from scada_gui.main_window import run_main_window

if __name__ == '__main__':
    # Ja modelis nav apmācīts, trenē
    if not os.path.exists('model/artifacts/model.pkl'):
        print("Modelis nav atrasts, uzsak trenesanu")
        train()
    else:
        print("Modelis eksiste, izlaizam trenesanu")

    # GUI startesana
    run_main_window()