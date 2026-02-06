from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    role: str

class BugBase(BaseModel):
    title: str
    body: str
    priority: Optional[str] = "medium"
    tags: Optional[str] = None

class BugCreate(BugBase):
    pass
class Prediction(BaseModel):
    predicted_developer: str
    confidence: float

class PredictionResponse(BaseModel):
    bug_id: Optional[int] = None
    predictions: List[Prediction]
    threshold: float
    is_auto_assigned: bool

class BugAssignmentResponse(BaseModel):
    developer_name: Optional[str] = None
    assignment_type: str
    assigned_at: datetime

    class Config:
        from_attributes = True

class BugResponse(BugBase):
    id: int
    status: str
    source: str
    created_at: datetime
    updated_at: datetime
    assignments: List[BugAssignmentResponse] = []
    predictions: List[Prediction] = []
    
    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_bugs: int
    auto_assigned: int
    manual_review: int
    bugs_per_developer: dict
    pending_bugs: int

class AssignmentUpdate(BaseModel):
    developer_id: Optional[int] = None
    developer_name: str
    notes: Optional[str] = None
