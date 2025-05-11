import logging
import os
from datetime import datetime
import json
import numpy as np
import pandas as pd
from .config import CONFIG

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.float32):
            return float(obj)
        return super(NumpyEncoder, self).default(obj)

def setup_logging():
    """Configure logging for the project"""
    log_dir = CONFIG['logging']['log_path']
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(
        log_dir, 
        f"{CONFIG['logging']['experiment_name']}.log"
    )
    
    logging.basicConfig(
        level=CONFIG['logging']['log_level'],
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def save_metrics(metrics_dict):
    """Save metrics to JSON file"""
    os.makedirs(os.path.dirname(CONFIG['artifacts']['metrics_path']), exist_ok=True)
    with open(CONFIG['artifacts']['metrics_path'], 'w') as f:
        json.dump(metrics_dict, f, cls=NumpyEncoder, indent=4)

def save_feature_importance(feature_names, importance_scores):
    """Save feature importance scores"""
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': importance_scores
    }).sort_values('importance', ascending=False)
    
    importance_df.to_csv(CONFIG['artifacts']['feature_importance_path'], index=False)