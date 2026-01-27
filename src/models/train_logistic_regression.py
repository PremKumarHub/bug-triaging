import numpy as np
import joblib
from pathlib import Path
from scipy.sparse import csr_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# =====================================================
# 1. PATHS
# =====================================================
BASE_DIR = Path(__file__).resolve().parents[2]
FEATURE_DIR = BASE_DIR / "data/features"
MODEL_DIR = BASE_DIR / "saved_models"
MODEL_DIR.mkdir(exist_ok=True)

# Load labels (to check integrity)
LABELS_FILE = FEATURE_DIR / "labels.npy"
LABEL_ENCODER_FILE = FEATURE_DIR / "label_encoder.pkl"

if not LABELS_FILE.exists():
    raise FileNotFoundError("Labels not found. Run vectorizer first.")

# =====================================================
# 2. LOAD DATA
# =====================================================
print("Loading data...")
loader = np.load(FEATURE_DIR / "tfidf_features.npz")
X = csr_matrix((loader["data"], loader["indices"], loader["indptr"]),
               shape=loader["shape"])
y = np.load(LABELS_FILE)

# Filtering rare classes for stratified split
unique, counts = np.unique(y, return_counts=True)
rare_classes = unique[counts < 2]
if len(rare_classes) > 0:
    mask = ~np.isin(y, rare_classes)
    X = X[mask]
    y = y[mask]

# Load class names for better reporting
encoder = joblib.load(LABEL_ENCODER_FILE)
target_names = encoder.classes_.astype(str)

print(f"   Data Shape: {X.shape}")

# =====================================================
# 3. SPLIT DATA
# =====================================================
print("Splitting Train/Test...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# =====================================================
# 4. TRAIN (OPTIMIZED)
# =====================================================
print("Training Logistic Regression (Optimized)...")

# IMPROVEMENTS:
# solver='saga': Faster for large sparse datasets (like TF-IDF text).
# C=10.0: Text often requires weaker regularization (higher C) to capture patterns.
# class_weight='balanced': Crucial for assigning bugs to less famous developers.
model = LogisticRegression(
    C=10.0,                 # Tuned for text (reduces underfitting)
    solver='saga',          # Best solver for sparse data
    class_weight='balanced',
    max_iter=1000,
    random_state=42
)

model.fit(X_train, y_train)

# =====================================================
# 5. EVALUATE
# =====================================================
print("Evaluating...")
y_pred = model.predict(X_test)

acc = accuracy_score(y_test, y_pred)
print(f"\nAccuracy: {acc:.2%}")

# Use unique labels in test set to avoid errors if some classes are missing in test
unique_labels = np.unique(np.concatenate((y_test, y_pred)))
print(classification_report(
    y_test, 
    y_pred, 
    labels=unique_labels,
    target_names=target_names[unique_labels], 
    zero_division=0
))

# =====================================================
# 6. SAVE
# =====================================================
save_path = MODEL_DIR / "logistic_regression.pkl"
joblib.dump(model, save_path)
print(f"Saved optimized model to: {save_path}")