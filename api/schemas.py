from pydantic import BaseModel
from typing import List

class BugReport(BaseModel):
    title: str
    body: str

class Prediction(BaseModel):
    developer: str
    confidence: float

class PredictionResponse(BaseModel):
    predictions: List[Prediction]
