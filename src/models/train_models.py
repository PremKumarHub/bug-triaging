import time
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
LOG_FILE = BASE_DIR / "training_log.txt"

def run_script(script_path):
    print(f"\n--- Running: {script_path.name} ---")
    start_time = time.time()
    result = subprocess.run(["python", str(script_path)], capture_output=True, text=True)
    end_time = time.time()
    
    if result.returncode == 0:
        print(f"SUCCESS: {script_path.name}")
        return end_time - start_time, result.stdout
    else:
        print(f"ERROR in {script_path.name}:\n{result.stderr}")
        return None, result.stderr

def main():
    scripts = [
        BASE_DIR / "src/feature_engineering/tfidf_vectorizer.py",
        BASE_DIR / "src/models/tune_hyperparameters.py",
        BASE_DIR / "src/models/train_ensemble.py"
    ]
    
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"\n\n--- PIPELINE RUN: {time.ctime()} ---\n")
        
        for script in scripts:
            duration, output = run_script(script)
            if duration:
                log.write(f"{script.name} completed in {duration:.2f}s\n")
                # Append last 5 lines of output to log for metrics
                log.write("\n".join(output.strip().split("\n")[-5:]) + "\n")
            else:
                log.write(f"{script.name} FAILED\n")
                break
                
    print(f"\nPipeline complete. Log written to {LOG_FILE}")

if __name__ == "__main__":
    main()
