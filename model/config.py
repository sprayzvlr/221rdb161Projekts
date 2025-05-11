from sklearn.ensemble import RandomForestClassifier

CONFIG = {
    'model_class': RandomForestClassifier,  # Modelis, kuru izmantot
    'model_params': {
        'n_estimators': 100,
        'max_depth': 5,
        'random_state': 42
    },
    'data': {
        'input_path': 'data/scada_data.csv',  # Oriģinālie dati
        'processed_path': 'data/processed.csv',  # Apstrādātie dati
        'test_size': 0.2,  # Testēšanas datu daļa
        'random_state': 42  # Pētniecības sēkla datu sadalījumam
    },
    'artifacts': {
        'model_path': 'model/model.pkl',  # Ceļš uz saglabāto modeli
        'scaler_path': 'model/scaler.pkl'  # Ceļš uz saglabāto skaleri
    }
}
