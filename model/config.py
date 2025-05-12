from sklearn.ensemble import RandomForestClassifier
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG = {
    'data': {
        'input_path': os.path.join(BASE_DIR, 'data', 'training_data.csv'),
        'processed_path': os.path.join(BASE_DIR, 'data', 'processed_data.csv'),
        'feature_columns': ['temp', 'pressure', 'flow'],
        'target_column': 'label',
        'test_size': 0.15,  # Samazinaju no 0.2 uz 0.15, lai vairāk datu izmantotu apmācībai
        'random_state': 42
    },
    'artifacts': {
        'base_path': os.path.join(BASE_DIR, 'model', 'artifacts'),
        'model_path': os.path.join(BASE_DIR, 'model', 'artifacts', 'model.pkl'),
        'scaler_path': os.path.join(BASE_DIR, 'model', 'artifacts', 'scaler.pkl')
    },
    'logging': {
        'log_path': os.path.join(BASE_DIR, 'logs')
    },
    'model_class': RandomForestClassifier
}

os.makedirs(CONFIG['artifacts']['base_path'], exist_ok=True)
os.makedirs(CONFIG['logging']['log_path'], exist_ok=True)
os.makedirs(os.path.dirname(CONFIG['data']['processed_path']), exist_ok=True)
