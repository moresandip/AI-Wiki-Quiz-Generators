from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class QuizRequest(BaseModel):
    url: Optional[str] = None
    topic: Optional[str] = None

class SaveResultsRequest(BaseModel):
    user_answers: Dict[str, Any]

class QuizResponse(BaseModel):
    id: int
    url: str
    title: Optional[str] = None
    summary: Optional[str] = None
    data: Dict[str, Any]  # The structured quiz data
    user_answers: Optional[Dict[str, Any]] = None  # User answers as JSON
    created_at: datetime

    class Config:
        orm_mode = True
