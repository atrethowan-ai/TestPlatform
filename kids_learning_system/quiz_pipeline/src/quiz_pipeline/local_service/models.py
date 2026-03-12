from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class AttemptPayload(BaseModel):
    attemptId: str = Field(...)
    childId: str = Field(...)
    quizId: str = Field(...)
    completedAt: str = Field(...)
    responses: Any = Field(...)
    score: Any = Field(...)
    metadata: Optional[Dict[str, Any]] = None

class AttemptListItem(BaseModel):
    filename: str
    attemptId: str
    quizId: str
    completedAt: str
