import numpy as np
import joblib
from pathlib import Path
from scipy.sparse import csr_matrix
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

BASE_DIR = Path(__file__).resolve().parents[2]
FEATURE_DIR = BASE_DIR / "data/features"
MODEL_DIR = BASE_DIR / "saved_models"
MODEL_DIR.mkdir(exist_ok=True)

# Load Data
loader = np.load(FEATURE_DIR / "tfidf_features.npz")
X = csr_matrix((loader["data"], loader["indices"], loader["indptr"]), shape=loader["shape"])
y = np.load(FEATURE_DIR / "labels.npy")

# Filtering rare classes for stratified split
unique, counts = np.unique(y, return_counts=True)
rare_classes = unique[counts < 2]
if len(rare_classes) > 0:
    mask = ~np.isin(y, rare_classes)
    X = X[mask]
    y = y[mask]

encoder = joblib.load(FEATURE_DIR / "label_encoder.pkl") # Load names

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Train
# alpha=1.0 is standard smoothing. 
# fit_prior=True learns which developers get more bugs naturally.
model = MultinomialNB(alpha=1.0, fit_prior=True)

print("Training Naive Bayes...")
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.2%}")

unique_labels = np.unique(np.concatenate((y_test, y_pred)))
print(classification_report(y_test, y_pred, labels=unique_labels, target_names=encoder.classes_[unique_labels], zero_division=0))

# Save
joblib.dump(model, MODEL_DIR / "naive_bayes.pkl")
print("Naive Bayes saved")