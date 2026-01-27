import json
import joblib
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder

# =====================================================
# 1. SETUP PATHS
# =====================================================
# Adjust BASE_DIR if your script is in a different subdirectory
BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "data/processed/bug_reports_nlp_ready.json"
FEATURE_DIR = BASE_DIR / "data/features"
FEATURE_DIR.mkdir(parents=True, exist_ok=True)

# Artifacts to save
TFIDF_MATRIX_FILE = FEATURE_DIR / "tfidf_features.npz"
TFIDF_VECTORIZER_FILE = FEATURE_DIR / "tfidf_vectorizer.pkl"
LABELS_FILE = FEATURE_DIR / "labels.npy"
LABEL_ENCODER_FILE = FEATURE_DIR / "label_encoder.pkl"

# =====================================================
# 2. LOAD AND PREPARE DATA
# =====================================================
print(f"Loading data from: {INPUT_FILE}")

try:
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"Error: File not found at {INPUT_FILE}")
    exit(1)

# Filter: Keep only issues that have BOTH text and an assignee
# (We cannot train on bugs with missing assignees)
valid_data = [
    item for item in data 
    if item.get("combined_text") and item.get("assignee")
]

texts = [item["combined_text"] for item in valid_data]
assignees = [item["assignee"] for item in valid_data]

print(f"Loaded {len(data)} raw documents")
print(f"Filtered to {len(texts)} valid training samples (with text & assignee)")

# =====================================================
# 3. ENCODE LABELS (ASSIGNEES)
# =====================================================
# Convert names like "roblourens" into numbers like 0, 1, 2...
print("Encoding assignee labels...")
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(assignees)

print(f"Found {len(label_encoder.classes_)} unique assignees")
# print("   Classes:", label_encoder.classes_[:5], "...") # Uncomment to see names

# =====================================================
# 4. TF-IDF FEATURE EXTRACTION
# =====================================================
print("Vectorizing text (this may take a moment)...")

vectorizer = TfidfVectorizer(
    max_features=30000,     # Increased from 20k to 30k
    ngram_range=(1, 3),     # Increased to capture more context
    min_df=2,               # Slightly more inclusive
    max_df=0.8,             # Slightly more exclusive
    sublinear_tf=True,
    stop_words='english'
)

X = vectorizer.fit_transform(texts)

print(f"Feature Matrix shape: {X.shape} (Rows, Features)")

# =====================================================
# 5. SAVE ARTIFACTS
# =====================================================
print("Saving artifacts to disk...")

# Save the sparse feature matrix (X)
np.savez_compressed(
    TFIDF_MATRIX_FILE,
    data=X.data,
    indices=X.indices,
    indptr=X.indptr,
    shape=X.shape
)

# Save the label vector (y)
np.save(LABELS_FILE, y)

# Save the processors (to use later on new data)
joblib.dump(vectorizer, TFIDF_VECTORIZER_FILE)
joblib.dump(label_encoder, LABEL_ENCODER_FILE)

print("DONE! All files saved to:", FEATURE_DIR)