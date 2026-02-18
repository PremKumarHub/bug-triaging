from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from api import schemas, crud
from database.db_connection import get_db
from src.prediction.assign_developer import assigner
from src.preprocessing.nlp_preprocessor import generate_tags
from typing import List
import json
import os
import random

from src.data_collection.github_collector import fetch_bugs_from_github

router = APIRouter()

async def process_bug_report(report: schemas.BugCreate, db: Session):
    """Helper to process a bug report: tag, save, predict, assign."""
    ASSIGNMENT_THRESHOLD = 0.40
    
    # 1. Generate auto-tags
    auto_tags = generate_tags(f"{report.title} {report.body}")

    # 2. Persist Bug with tags
    db_bug = crud.create_bug(db, report, tags=auto_tags)
    
    # 3. Get Prediction
    results = assigner.predict(report.title, report.body)
    if not results:
        return None, "Model not loaded or prediction failed"
    
    # 4. Decision Logic
    top_prediction = results[0]
    is_auto_assigned = top_prediction["confidence"] >= ASSIGNMENT_THRESHOLD
    
    # 5. Save Prediction Result
    res_payload = {
        "predictions": results,
        "threshold": ASSIGNMENT_THRESHOLD,
        "is_auto_assigned": is_auto_assigned,
        "tags": auto_tags
    }
    crud.create_prediction(db, db_bug.id, res_payload, ASSIGNMENT_THRESHOLD)
    
    # 6. Handle Assignment
    if is_auto_assigned:
        crud.create_assignment(db, db_bug.id, top_prediction["predicted_developer"], "auto")
    else:
        crud.create_assignment(db, db_bug.id, top_prediction["predicted_developer"], "manual")
        
    return {
        "bug_id": db_bug.id,
        "predictions": results,
        "threshold": ASSIGNMENT_THRESHOLD,
        "is_auto_assigned": is_auto_assigned,
        "title": report.title
    }, None

@router.post("/predict", response_model=schemas.PredictionResponse)
async def predict_assignee(report: schemas.BugCreate, db: Session = Depends(get_db)):
    try:
        result, error = await process_bug_report(report, db)
        if error:
            raise HTTPException(status_code=500, detail=error)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fetch-github")
async def fetch_github_issues(req: schemas.GithubFetchRequest, db: Session = Depends(get_db)):
    try:
        # 1. Fetch from GitHub
        # We use the total count requested
        raw_issues = fetch_bugs_from_github(total_limit=req.count, state="open")
        
        imported = []
        skipped = []
        errors = []
        
        for issue in raw_issues:
            # 2. Check for duplicates by title
            existing = crud.get_bug_by_title(db, issue["title"])
            if existing:
                skipped.append(issue["title"])
                continue
            
            # 3. Process new bug
            report = schemas.BugCreate(
                title=issue["title"],
                body=issue["body"],
                priority="medium",
                source="github"
            )
            
            result, error = await process_bug_report(report, db)
            if error:
                errors.append({"title": issue["title"], "error": error})
            else:
                imported.append(result)
                
        return {
            "total_fetched": len(raw_issues),
            "imported_count": len(imported),
            "skipped_count": len(skipped),
            "error_count": len(errors),
            "imported": imported,
            "skipped_titles": skipped,
            "errors": errors
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import-local")
async def import_local_bugs(req: schemas.LocalImportRequest, db: Session = Depends(get_db)):
    try:
        # Resolve path relative to project root
        # The file is at c:\Users\Prem\Desktop\final yer project document\Bug Triaging\Bug-Triaging-ML-System\data\processed\bug_reports_cleaned.json
        # routes.py is at ...\api\routes.py
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(base_dir, "data", "processed", "bug_reports_cleaned.json")
        
        if not os.path.exists(data_path):
            raise HTTPException(status_code=404, detail=f"Local data file not found at {data_path}")
        
        with open(data_path, 'r', encoding='utf-8') as f:
            all_bugs = json.load(f)
        
        # Take a sample to avoid duplicates and test variety
        count = min(len(all_bugs), req.count)
        sampled = random.sample(all_bugs, count)
        
        imported = []
        skipped = []
        errors = []
        
        for bug in sampled:
            # 1. Check for duplicates
            existing = crud.get_bug_by_title(db, bug["title"])
            if existing:
                skipped.append(bug["title"])
                continue
            
            # 2. Process
            report = schemas.BugCreate(
                title=bug["title"],
                body=bug["body"],
                priority="medium",
                source="local"
            )
            
            result, error = await process_bug_report(report, db)
            if error:
                errors.append({"title": bug["title"], "error": error})
            else:
                imported.append(result)
                
        return {
            "total_sampled": len(sampled),
            "imported_count": len(imported),
            "skipped_count": len(skipped),
            "error_count": len(errors),
            "imported": imported,
            "skipped_titles": skipped,
            "errors": errors
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

@router.post("/bugs/bulk-delete")
async def bulk_delete_bugs(req: schemas.BulkDeleteRequest, db: Session = Depends(get_db)):
    count = crud.delete_bugs(db, req.bug_ids)
    return {"message": f"Successfully deleted {count} bugs"}

@router.get("/health")
async def health_check():
    if assigner.model and assigner.vectorizer and assigner.encoder:
        return {"status": "healthy", "model_loaded": True}
    return {"status": "unhealthy", "model_loaded": False}
