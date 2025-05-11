import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from imblearn.over_sampling import SMOTE
import joblib
from model.config import CONFIG


def prepare_data():
    """
    Sagatavo datus apmācībai - attīra, standartizē un saglabā apstrādātos datus.
    """
    df = pd.read_csv(CONFIG['data']['input_path'], parse_dates=['timestamp'])

    # Pārliecināties, ka visi nepieciešamie lauki ir datu ietvarā
    required_columns = ['temp', 'pressure', 'flow', 'label']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"Trūkst nepieciešamie lauki: {', '.join(required_columns)}")

    # Datu attīrīšana (fillna)
    df = df.ffill()

    features = df[['temp', 'pressure', 'flow']]
    target = df['label']

    # Skalēšana
    scaler = StandardScaler()
    scaled_features = pd.DataFrame(scaler.fit_transform(features), columns=features.columns)

    # Saglabā apstrādātos datus un skalēšanas modeli
    scaled_features.to_csv(CONFIG['data']['processed_path'], index=False)
    joblib.dump(scaler, CONFIG['artifacts']['scaler_path'])

    return scaled_features, target


def train():
    """
    Apmāca modeli un veic novērtēšanu
    """
    # Sagatavo datus
    X, y = prepare_data()

    # Sadalījums apmācībai un testēšanai
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=CONFIG['data']['test_size'],
        random_state=CONFIG['data']['random_state']
    )

    # Datu sabalansēšana ar SMOTE
    smote = SMOTE(random_state=42)
    X_train, y_train = smote.fit_resample(X_train, y_train)

    # Modeļa apmācība
    model_cls = CONFIG['model_class']
    model = model_cls(**CONFIG['model_params'])
    model.fit(X_train, y_train)

    # Saglabā modeli
    joblib.dump(model, CONFIG['artifacts']['model_path'])
    print(f"Model trained and saved to {CONFIG['artifacts']['model_path']}")

    # Novērtēšana uz testa datiem
    y_pred = model.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")
    print("Confusion matrix:\n", confusion_matrix(y_test, y_pred))
    print("Classification report:\n", classification_report(y_test, y_pred))


if __name__ == '__main__':
    train()
