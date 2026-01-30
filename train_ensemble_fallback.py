import numpy as np
import joblib
from pathlib import Path
from scipy.sparse import csr_matrix
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import VotingClassifier

BASE_DIR = Path(__file__).resolve().parent
FEATURE_DIR = BASE_DIR / "data/features"
MODEL_DIR = BASE_DIR / "saved_models"

def load_data():
    loader = np.load(FEATURE_DIR / "tfidf_features.npz")
    X = csr_matrix((loader["data"], loader["indices"], loader["indptr"]), shape=loader["shape"])
    y = np.load(FEATURE_DIR / "labels.npy")
    return X, y

def train_fallback():
    print("Loading data...")
    X, y = load_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("Loading LinearSVM...")
    try:
        svm_best = joblib.load(MODEL_DIR / "linear_svm.pkl")
    except FileNotFoundError:
        print("LinearSVM not found, skipping fallback.")
        return

    print("Calibrating SVM (Fast)...")
    # Using cv=3 because 'prefit' caused validation error in this env
    svm_calibrated = CalibratedClassifierCV(svm_best, method='sigmoid', cv=3)
    
    # We fit the calibrator? If prefit, we fit on X_train?
    # correct usage for prefit: svm_calibrated.fit(X_train, y_train) (Wait, docs say if prefit, fit does nothing? No)
    # Docs: "If cv='prefit', the classifier must have been fitted already."
    # "The fit method will calibrate... based on the input data."
    svm_calibrated.fit(X_train, y_train)

    print("Creating Single-Model Ensemble...")
    # VotingClassifier with one model just allows consistent API (predict_proba)
    ensemble = VotingClassifier(
        estimators=[('svm', svm_calibrated)],
        voting='soft',
        n_jobs=-1
    )
    
    ensemble.fit(X_train, y_train)
    
    print("Saving Ensemble...")
    joblib.dump(ensemble, MODEL_DIR / "ensemble_model.pkl")
    print("Ensemble saved!")

if __name__ == "__main__":
    train_fallback()
