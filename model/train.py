import pandas as pd
import os
import logging
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

import joblib
from model.config import CONFIG
import numpy as np

from imblearn.over_sampling import SMOTE

def setup_logging():
    log_dir = CONFIG['logging']['log_path']
    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def prepare_data(generate_more_samples=True, target_samples=1000):
    from imblearn.over_sampling import SMOTE
    logger = setup_logging()

    # Load and prepare data
    df = pd.read_csv(CONFIG['data']['input_path'])

    # Extract features and target
    X = df[CONFIG['data']['feature_columns']]
    y = df[CONFIG['data']['target_column']]

    # Scale features
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(
        scaler.fit_transform(X),
        columns=X.columns
    )

    # Save processed data for evaluation
    processed_df = X_scaled.copy()
    processed_df.to_csv(CONFIG['data']['processed_path'], index=False)

    # Apply SMOTE for balance
    try:
        logger.info(f"Original dataset size: {len(X)} samples")
        
        if generate_more_samples and len(X) < target_samples:
            from imblearn.over_sampling import SMOTE, ADASYN, BorderlineSMOTE
            import numpy as np
            
            # Standarta SMOTE
            smote = SMOTE(random_state=42)
            X_smote, y_smote = smote.fit_resample(X_scaled, y)
            
            # ADASYN - adapts the synthetic sample generation for each minority class
            adasyn = ADASYN(random_state=43)
            X_adasyn, y_adasyn = adasyn.fit_resample(X_scaled, y)
            
            # BorderlineSMOTE - focuses on samples near the boundary
            bsmote = BorderlineSMOTE(random_state=44)
            X_bsmote, y_bsmote = bsmote.fit_resample(X_scaled, y)
            
            # Apvieno visus sintētiskos datus
            X_combined = pd.concat([
                pd.DataFrame(X_smote, columns=X.columns),
                pd.DataFrame(X_adasyn, columns=X.columns),
                pd.DataFrame(X_bsmote, columns=X.columns)
            ])
            
            y_combined = pd.concat([
                pd.Series(y_smote),
                pd.Series(y_adasyn),
                pd.Series(y_bsmote)
            ])
            
            # Ņem unikālus paraugus (novērš duplikātus)
            combined_data = pd.concat([X_combined, y_combined.reset_index(drop=True)], axis=1)
            combined_data = combined_data.drop_duplicates()
            
            # Ierobežo kopējo paraugu skaitu, ja tas pārsniedz mērķi
            if len(combined_data) > target_samples:
                combined_data = combined_data.sample(target_samples, random_state=42)
            
            # Atdala features un target atpakaļ
            X_balanced = combined_data[X.columns]
            y_balanced = combined_data[y.name]
            
            logger.info(f"Generated dataset with {len(X_balanced)} samples using multiple oversampling techniques")
            
            return X_balanced, y_balanced, scaler
        else:
            # Standarta SMOTE
            smote = SMOTE(random_state=42)
            X_balanced, y_balanced = smote.fit_resample(X_scaled, y)
            logger.info(f"Generated dataset with {len(X_balanced)} samples using standard SMOTE")
            return pd.DataFrame(X_balanced, columns=X.columns), pd.Series(y_balanced), scaler
    except ValueError as e:
        logger.warning(f"SMOTE failed: {e}. Using original data.")
        return X_scaled, y, scaler



def train(target_samples=1000):
    """
    Trenē mašīnmācības modeli ar iespēju ģenerēt vairāk sintētisko datu.
    
    :param target_samples: cik paraugus mērķēt ģenerēt apmācībai (noklusējums: 1000)
    :return: apmācītais modelis un datu skalētājs
    """
    logger = setup_logging()
    logger.info(f"Starting model training with target {target_samples} samples...")

    # Prepare data with more samples
    X, y, scaler = prepare_data(generate_more_samples=True, target_samples=target_samples)

    # Ensure we have enough samples
    n_samples = len(y)
    if n_samples < 4:  # absolute minimum needed for splitting
        raise ValueError(f"Not enough samples to split data. Got {n_samples} samples.")

    # Calculate minimum test size
    min_test_samples = max(1, int(n_samples * 0.1))  # at least 1 sample or 10%
    actual_test_size = min_test_samples / n_samples

    try:
        # First try with stratification
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=actual_test_size,
            random_state=42,
            shuffle=True
        )
    except ValueError as e:
        logger.warning(f"Initial split failed: {e}")
        # If that fails, try without stratification
        indices = np.arange(n_samples)
        train_idx, test_idx = train_test_split(
            indices,
            test_size=actual_test_size,
            random_state=42
        )
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    # Initialize and train model with improved hyperparameters
    model = CONFIG['model_class'](
        n_estimators=500,  # Palielināts no 200 uz 500
        max_depth=15,      # Palielināts no 10 uz 15
        min_samples_split=2,
        min_samples_leaf=1,
        class_weight='balanced',
        random_state=42,
        bootstrap=True,    # Bootstrapping uzlabos dažādību
        n_jobs=-1          # Izmantot visus pieejamos procesora kodolus
    )
    
    # Train model
    print(f"Training model on {len(X_train)} samples...")
    model.fit(X_train, y_train)

    # Save model and scaler
    os.makedirs(CONFIG['artifacts']['base_path'], exist_ok=True)
    joblib.dump(model, CONFIG['artifacts']['model_path'])
    joblib.dump(scaler, CONFIG['artifacts']['scaler_path'])

    # Evaluate
    y_pred = model.predict(X_test)

    # Print metrics only if we have test samples
    if len(y_test) > 0:
        print(f"Model trained on {len(X_train)} samples and tested on {len(X_test)} samples")
        print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")
        print(f"Confusion matrix:\n {confusion_matrix(y_test, y_pred)}")
        print(f"Classification report:\n {classification_report(y_test, y_pred)}")
        
        # Parāda F1 score, kas ir svarīgs balansētai klasifikācijai
        from sklearn.metrics import f1_score
        f1 = f1_score(y_test, y_pred, average='weighted')
        print(f"Weighted F1 Score: {f1:.4f}")
    else:
        print("Warning: No test samples available for evaluation")

    return model, scaler


if __name__ == '__main__':
    import argparse
    
    # Pievieno komandlīnijas argumentu apstrādi
    parser = argparse.ArgumentParser(description='Train the anomaly detection model')
    parser.add_argument('--samples', type=int, default=1000, 
                        help='Target number of samples to generate (default: 1000)')
    
    args = parser.parse_args()
    
    # Trenē modeli ar norādīto paraugu skaitu
    train(target_samples=args.samples)
