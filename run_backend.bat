@echo off
cd /d c:\Users\Public\Documents\bug-triaging
python -m uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
