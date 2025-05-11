from scada_gui.main_window import run_main_window
import argparse

if __name__ == '__main__':
    # Pievieno komandlīnijas argumentu apstrādi
    parser = argparse.ArgumentParser(description='Start SCADA system with model training options')
    parser.add_argument('--retrain', action='store_true', help='Force model retraining')
    parser.add_argument('--samples', type=int, default=1000, 
                        help='Target number of samples for model training (default: 1000)')
    
    args = parser.parse_args()
    
    # Pārbauda vai ir nepieciešams trenēt modeli
    if not os.path.exists('model/artifacts/model.pkl') or args.retrain:
        print(f"{'Model not found. Training' if not os.path.exists('model/artifacts/model.pkl') else 'Retraining'} model with {args.samples} samples...")
        train(target_samples=args.samples)
    else:
        print("Model already exists. Skipping training.")

    # Startē GUI
    run_main_window()
