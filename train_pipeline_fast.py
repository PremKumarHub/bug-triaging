import subprocess
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def run_script(script_path):
    print(f"\n--- Running: {script_path.name} ---")
    start_time = time.time()
    result = subprocess.run(["python", str(script_path)], capture_output=True, text=True)
    end_time = time.time()
    
    if result.returncode == 0:
        print(f"SUCCESS: {script_path.name}")
        print("Output:\n" + result.stdout)
    else:
        print(f"ERROR in {script_path.name}:\n{result.stderr}")
        exit(1)

def main():
    scripts = [
        BASE_DIR / "src/feature_engineering/tfidf_vectorizer.py",
        BASE_DIR / "src/models/train_base_models.py", 
        BASE_DIR / "src/models/train_ensemble.py"
    ]
    
    for script in scripts:
        run_script(script)
        
    print("\nFat Training Pipeline Completed Successfully.")

if __name__ == "__main__":
    main()
