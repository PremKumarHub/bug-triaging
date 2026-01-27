import joblib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
VECTORIZER_PATH = BASE_DIR / "data/features/tfidf_vectorizer.pkl"

vectorizer = joblib.load(VECTORIZER_PATH)

print("Vectorizer loaded")
print("Total features:", len(vectorizer.vocabulary_))

# Show some feature names
features = list(vectorizer.vocabulary_.keys())
print("Sample features:", features[:30])
