import numpy as np
import joblib
from pathlib import Path
from scipy.sparse import csr_matrix
from sklearn.ensemble import VotingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

BASE_DIR = Path(__file__).resolve().parents[2]
FEATURE_DIR = BASE_DIR / "data/features"
MODEL_DIR = BASE_DIR / "saved_models"

def load_data():
    loader = np.load(FEATURE_DIR / "tfidf_features.npz")
    X = csr_matrix((loader["data"], loader["indices"], loader["indptr"]), shape=loader["shape"])
    y = np.load(FEATURE_DIR / "labels.npy")
    
    unique, counts = np.unique(y, return_counts=True)
    rare_classes = unique[counts < 2]
    if len(rare_classes) > 0:
        mask = ~np.isin(y, rare_classes)
        X = X[mask]
        y = y[mask]
    
    return X, y

def train_ensemble():
    X, y = load_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Load best-tuned models
    lr = joblib.load(MODEL_DIR / "logistic_regression_best.pkl")
    rf = joblib.load(MODEL_DIR / "random_forest_best.pkl")
    svm = joblib.load(MODEL_DIR / "linear_svm_best.pkl")
    
    # LinearSVC doesn't support predict_proba by default, so we might use CalibratedClassifierCV
    # if we want soft voting. For now, we'll use hard voting.
    ensemble = VotingClassifier(
        estimators=[
            ('lr', lr),
            ('rf', rf),
            ('svm', svm)
        ],
        voting='hard'
    )
    
    print("Training Ensemble Model (Voting Classifier)...")
    ensemble.fit(X_train, y_train)
    
    y_pred = ensemble.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nEnsemble Accuracy: {acc:.2%}")
    
    # Save ensemble
    joblib.dump(ensemble, MODEL_DIR / "ensemble_model.pkl")
    print(f"Ensemble model saved to {MODEL_DIR / 'ensemble_model.pkl'}")

if __name__ == "__main__":
    train_ensemble()
