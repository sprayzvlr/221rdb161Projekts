import pandas as pd
import joblib
from model.config import CONFIG


def load_artifacts():
    model = joblib.load(CONFIG['artifacts']['model_path'])
    scaler = joblib.load(CONFIG['artifacts']['scaler_path'])
    return model, scaler


def predict(sample: dict):
    """
    Makes prediction for a single sample
    sample = {'temp': float, 'pressure': float, 'flow': float}
    """
    model, scaler = load_artifacts()

    # Create DataFrame with proper column names
    sample_df = pd.DataFrame([sample], columns=['temp', 'pressure', 'flow'])

    # Scale the features
    X_scaled = pd.DataFrame(
        scaler.transform(sample_df),
        columns=['temp', 'pressure', 'flow']
    )

    # Debug - print scaled values
    print(f"Scaled input: {X_scaled.values}")
    
    # For debugging, get prediction probability
    if hasattr(model, 'predict_proba'):
        probs = model.predict_proba(X_scaled)
        print(f"Prediction probabilities: {probs}")
    
    # Make prediction
    prediction = model.predict(X_scaled)[0]
    print(f"Model prediction: {prediction}")
    
    return prediction
