from pydantic import BaseModel
from typing import List, Optional

class Response(BaseModel):
    questionId: str
    answer: Union[str, List[str]]
    submittedAt: str
    isCorrect: Optional[bool] = None
    score: Optional[int] = None
    manualReviewRequired: Optional[bool] = None

class Attempt(BaseModel):
    id: str
    quizId: str
    childId: str
    startedAt: str
    completedAt: Optional[str] = None
    responses: List[Response]
    score: Optional[dict] = None
    manualReviewRequired: Optional[bool] = None
