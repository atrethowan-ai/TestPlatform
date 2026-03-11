from pydantic import BaseModel
from typing import List

class AnalysisArtifact(BaseModel):
    id: str
    childId: str
    quizId: str
    createdAt: str
    summary: str
    weaknesses: List[str]
    recommendations: List[str]
