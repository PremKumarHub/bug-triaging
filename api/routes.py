from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from api import schemas, crud
from database.db_connection import get_db
from src.prediction.assign_developer import assigner
from typing import List

router = APIRouter()

@router.post("/predict", response_model=schemas.PredictionResponse)
async def predict_assignee(report: schemas.BugCreate, db: Session = Depends(get_db)):
    ASSIGNMENT_THRESHOLD = 0.40
    try:
        # 1. Persist Bug
        db_bug = crud.create_bug(db, report)
        
        # 2. Get Prediction
        results = assigner.predict(report.title, report.body)
        if not results:
            raise HTTPException(status_code=500, detail="Model not loaded or prediction failed")
        
        # 3. Decision Logic
        top_prediction = results[0]
        is_auto_assigned = top_prediction["confidence"] >= ASSIGNMENT_THRESHOLD
        
        # 4. Save Prediction Result
        res_payload = {
            "predictions": results,
            "threshold": ASSIGNMENT_THRESHOLD,
            "is_auto_assigned": is_auto_assigned
        }
        crud.create_prediction(db, db_bug.id, res_payload, ASSIGNMENT_THRESHOLD)
        
        # 5. Handle Assignment
        if is_auto_assigned:
            crud.create_assignment(db, db_bug.id, top_prediction["predicted_developer"], "auto")
        else:
            crud.create_assignment(db, db_bug.id, top_prediction["predicted_developer"], "manual")
            
        return {
            "bug_id": db_bug.id,
            "predictions": results,
            "threshold": ASSIGNMENT_THRESHOLD,
            "is_auto_assigned": is_auto_assigned
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bugs", response_model=List[schemas.BugResponse])
async def read_bugs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    bugs = crud.get_bugs(db, skip=skip, limit=limit)
    return bugs

@router.get("/stats", response_model=schemas.DashboardStats)
async def read_stats(db: Session = Depends(get_db)):
    return crud.get_dashboard_stats(db)

@router.get("/users", response_model=List[schemas.UserBase])
async def read_users(role: str = None, db: Session = Depends(get_db)):
    return crud.get_users(db, role=role)

@router.get("/bugs/{bug_id}/predictions")
async def read_bug_predictions(bug_id: int, db: Session = Depends(get_db)):
    pred = crud.get_prediction_by_bug(db, bug_id)
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")
    import json
    return {
        "bug_id": bug_id,
        "predictions": json.loads(pred.top_alternatives),
        "threshold": pred.threshold_used
    }

@router.post("/bugs/{bug_id}/assign")
async def manual_assign(bug_id: int, update: schemas.AssignmentUpdate, db: Session = Depends(get_db)):
    crud.create_assignment(db, bug_id, update.developer_name, "manual", update.developer_id)
    return {"message": "Assignment updated successfully"}

@router.delete("/bugs/{bug_id}")
async def delete_bug(bug_id: int, db: Session = Depends(get_db)):
    success = crud.delete_bug(db, bug_id)
    if not success:
        raise HTTPException(status_code=404, detail="Bug not found")
    return {"message": "Bug deleted successfully"}

@router.get("/health")
async def health_check():
    if assigner.model and assigner.vectorizer and assigner.encoder:
        return {"status": "healthy", "model_loaded": True}
    return {"status": "unhealthy", "model_loaded": False}
