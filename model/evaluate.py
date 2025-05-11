import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import joblib
from model.config import CONFIG
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import os

def load_artifacts():
    """
    Ielādē modeli un skaleri.
    """
    model_path = CONFIG['artifacts']['model_path']
    scaler_path = 'model/scaler.pkl'

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")
    if not os.path.exists(scaler_path):
        raise FileNotFoundError(f"Scaler file not found at {scaler_path}")

    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)

    return model, scaler

def evaluate():
    # Ielādē apstrādātos datus
    df = pd.read_csv(CONFIG['data']['processed_path'])

    # Iegūst features un label
    X = df.values
    y = pd.read_csv(CONFIG['data']['input_path'])['label']

    # Ielādē modeli un skaleri
    model, scaler = load_artifacts()

    # Skalē datus, ja skalers tika izmantots apmācībā
    X_scaled = scaler.transform(X)

    # Sadalījums treniņam un testiem
    _, X_test, _, y_test = train_test_split(X_scaled, y,
                                            test_size=CONFIG['data']['test_size'],
                                            random_state=CONFIG['data']['random_state'])

    # Prognoze
    y_pred = model.predict(X_test)

    # Iespiest rezultātus
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Confusion matrix:\n", confusion_matrix(y_test, y_pred))
    print("Classification report:\n", classification_report(y_test, y_pred))

if __name__ == '__main__':
    evaluate()
