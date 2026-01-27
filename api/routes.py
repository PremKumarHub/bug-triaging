from fastapi import APIRouter, HTTPException
from api.schemas import BugReport, PredictionResponse
from src.prediction.assign_developer import assigner

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse)
async def predict_assignee(report: BugReport):
    try:
        results = assigner.predict(report.title, report.body)
        if not results:
            raise HTTPException(status_code=500, detail="Model not loaded or prediction failed")
        return {"predictions": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    if assigner.model and assigner.vectorizer and assigner.encoder:
        return {"status": "healthy", "model_loaded": True}
    return {"status": "unhealthy", "model_loaded": False}
