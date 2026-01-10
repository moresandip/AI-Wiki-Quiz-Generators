from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class QuizRequest(BaseModel):
    url: str

class QuizResponse(BaseModel):
    id: int
    url: str
    title: Optional[str] = None
    summary: Optional[str] = None
    data: Dict[str, Any]  # The structured quiz data
    created_at: datetime

    class Config:
        orm_mode = True
