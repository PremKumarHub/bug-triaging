import numpy as np
from scipy.sparse import csr_matrix
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
NPZ_PATH = BASE_DIR / "data/features/tfidf_features.npz"

loader = np.load(NPZ_PATH)

X = csr_matrix(
    (loader["data"], loader["indices"], loader["indptr"]),
    shape=loader["shape"]
)

print("TF-IDF matrix loaded")
print("Shape (documents x features):", X.shape)
print("Non-zero values:", X.nnz)
print("Sparsity (%):", 100 * (1 - X.nnz / (X.shape[0] * X.shape[1])))
    