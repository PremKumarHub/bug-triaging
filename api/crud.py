from sqlalchemy.orm import Session
from api import models, schemas
import json

def get_bug(db: Session, bug_id: int):
    return db.query(models.Bug).filter(models.Bug.id == bug_id).first()

def get_bug_by_title(db: Session, title: str):
    return db.query(models.Bug).filter(models.Bug.title == title).first()

from sqlalchemy.orm import Session, joinedload

def get_bugs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Bug).options(
        joinedload(models.Bug.assignments),
        joinedload(models.Bug.predictions)
    ).offset(skip).limit(limit).all()

def create_bug(db: Session, bug: schemas.BugCreate, tags: str = None):
    bug_data = bug.dict()
    if tags:
        bug_data["tags"] = tags
    db_bug = models.Bug(**bug_data)
    db.add(db_bug)
    db.commit()
    db.refresh(db_bug)
    return db_bug

def create_prediction(db: Session, bug_id: int, prediction: dict, threshold: float):
    db_prediction = models.ModelPrediction(
        bug_id=bug_id,
        predicted_developer=prediction["predictions"][0]["predicted_developer"],
        confidence=prediction["predictions"][0]["confidence"],
        top_alternatives=json.dumps(prediction["predictions"]),
        threshold_used=threshold
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction

def create_assignment(db: Session, bug_id: int, developer_name: str, assignment_type: str, developer_id: int = None):
    db_assignment = models.BugAssignment(
        bug_id=bug_id,
        developer_id=developer_id,
        developer_name=developer_name,
        assignment_type=assignment_type
    )
    db.add(db_assignment)
    
    # Update bug status
    bug = db.query(models.Bug).filter(models.Bug.id == bug_id).first()
    if assignment_type == 'auto':
        bug.status = 'assigned'
    else:
        bug.status = 'manual-review'
    
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

def get_dashboard_stats(db: Session):
    total = db.query(models.Bug).count()
    auto = db.query(models.BugAssignment).filter(models.BugAssignment.assignment_type == 'auto').count()
    manual = db.query(models.BugAssignment).filter(models.BugAssignment.assignment_type == 'manual').count()
    pending = db.query(models.Bug).filter(models.Bug.status == 'open').count()
    
    # Bugs per developer
    # Note: Simplified for now
    dev_counts = {}
    assignments = db.query(models.BugAssignment).all()
    for a in assignments:
        dev = a.developer_name
        dev_counts[dev] = dev_counts.get(dev, 0) + 1
        
    return {
        "total_bugs": total,
        "auto_assigned": auto,
        "manual_review": manual,
        "bugs_per_developer": dev_counts,
        "pending_bugs": pending
    }

def get_users(db: Session, role: str = None):
    query = db.query(models.User)
    if role:
        query = query.filter(models.User.role == role)
    return query.all()

def get_prediction_by_bug(db: Session, bug_id: int):
    return db.query(models.ModelPrediction).filter(models.ModelPrediction.bug_id == bug_id).first()

def delete_bug(db: Session, bug_id: int):
    db_bug = db.query(models.Bug).filter(models.Bug.id == bug_id).first()
    if db_bug:
        db.delete(db_bug)
        db.commit()
        return True
    return False
