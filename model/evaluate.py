import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import joblib
from model.config import CONFIG
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import os

def load_artifacts():
    """
    Loads model and scaler artifacts.
    """
    model_path = CONFIG['artifacts']['model_path']
    scaler_path = CONFIG['artifacts']['scaler_path']

    # Create artifacts directory if it doesn't exist
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")
    if not os.path.exists(scaler_path):
        raise FileNotFoundError(f"Scaler file not found at {scaler_path}")

    try:
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        return model, scaler
    except Exception as e:
        raise RuntimeError(f"Error loading artifacts: {str(e)}")



def evaluate():
    try:
        # Ielādē apstrādātos datus
        df = pd.read_csv(CONFIG['data']['processed_path'])
        
        # Iegūst features un label
        X = df
        y = pd.read_csv(CONFIG['data']['input_path'])[CONFIG['data']['target_column']]
        
        # Ielādē modeli un skaleri
        model, scaler = load_artifacts()
        
        # Sadalījums treniņam un testiem
        _, X_test, _, y_test = train_test_split(
            X, y,
            test_size=CONFIG['data']['test_size'],
            random_state=CONFIG['data']['random_state'])
        
        # Prognoze
        y_pred = model.predict(X_test)
        
        # Aprēķina metriku
        accuracy = accuracy_score(y_test, y_pred)
        conf_matrix = confusion_matrix(y_test, y_pred)
        report = classification_report(y_test, y_pred)
        
        # Iespiest rezultātus
        print("Accuracy:", accuracy)
        print("Confusion matrix:\n", conf_matrix)
        print("Classification report:\n", report)
        
        # Return metrics for GUI display
        return {
            'accuracy': accuracy,
            'confusion_matrix': conf_matrix,
            'report': report,
            'test_size': len(y_test)
        }
    except FileNotFoundError as e:
        print(f"Error: File not found - {str(e)}")
        raise
    except Exception as e:
        print(f"Error during evaluation: {str(e)}")
        raise

if __name__ == '__main__':
    evaluate()
