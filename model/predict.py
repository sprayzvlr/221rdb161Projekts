import pandas as pd
import joblib

def load_artifacts():
    model = joblib.load('model/model.pkl')
    scaler = joblib.load('model/scaler.pkl')
    return model, scaler

def predict(sample: dict):
    """
    sample = {'temp': float, 'pressure': float, 'flow': float}
    """
    model, scaler = load_artifacts()

    # Convert the input sample into a pandas DataFrame with explicit column names
    sample_df = pd.DataFrame([sample], columns=['temp', 'pressure', 'flow'])

    # Apply scaling
    X = scaler.transform(sample_df)

    # Predict using the model
    return model.predict(X)[0]