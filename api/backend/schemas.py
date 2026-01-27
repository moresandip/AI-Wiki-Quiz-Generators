from pydantic import BaseModel
from typing import Optional

class QuizRequest(BaseModel):
    url: str

class QuizResponse(BaseModel):
    id: Optional[int] = None
    url: str
    title: str
    summary: str
    data: dict
    created_at: str
