from fastapi import APIRouter, HTTPException
from api.schemas import BugReport, PredictionResponse
from src.prediction.assign_developer import assigner

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse)
async def predict_assignee(report: BugReport):
    ASSIGNMENT_THRESHOLD = 0.50
    try:
        results = assigner.predict(report.title, report.body)
        if not results:
            raise HTTPException(status_code=500, detail="Model not loaded or prediction failed")
        
        # Logic: Auto-assign if top prediction exceeds threshold
        is_auto_assigned = results[0]["confidence"] >= ASSIGNMENT_THRESHOLD
        
        return {
            "predictions": results,
            "threshold": ASSIGNMENT_THRESHOLD,
            "is_auto_assigned": is_auto_assigned
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    if assigner.model and assigner.vectorizer and assigner.encoder:
        return {"status": "healthy", "model_loaded": True}
    return {"status": "unhealthy", "model_loaded": False}
