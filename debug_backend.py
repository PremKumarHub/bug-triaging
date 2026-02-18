
import sys
import os
from pathlib import Path

# Add project root to path
base_dir = Path(__file__).resolve().parent
sys.path.append(str(base_dir))

from database.db_connection import SessionLocal
from api import models
from src.prediction.assign_developer import assigner

def debug_info():
    db = SessionLocal()
    try:
        bug_count = db.query(models.Bug).count()
        print(f"Total bugs in database: {bug_count}")
        
        print(f"Model loaded: {assigner.model is not None}")
        print(f"Vectorizer loaded: {assigner.vectorizer is not None}")
        print(f"Encoder loaded: {assigner.encoder is not None}")
        
        if assigner.model is None:
            print("Trying to load model...")
            assigner._load_model()
            print(f"Model loaded after retry: {assigner.model is not None}")
            
        # Check for GitHub token
        token = os.getenv("GITHUB_PAT")
        print(f"GITHUB_PAT set: {token is not None and len(token) > 0}")
        
    finally:
        db.close()

if __name__ == "__main__":
    debug_info()
