from pydantic import BaseModel, Field
from typing import List, Optional, Union

class AuthoringQuestion(BaseModel):
    id: str
    type: str
    prompt: str
    mediaRef: Optional[str] = None
    choices: Optional[List[str]] = None
    answerKey: Optional[Union[str, List[str]]] = None
    distractors: Optional[List[str]] = None
    rubricRef: Optional[str] = None
    domain: Optional[str] = None
    audioText: Optional[str] = None
    ttsStyle: Optional[str] = None
    imageSpec: Optional[str] = None

class AuthoringSection(BaseModel):
    id: str
    title: str
    questions: List[AuthoringQuestion]

class AuthoringQuiz(BaseModel):
    id: str
    title: str
    ageGroup: str
    sections: List[AuthoringSection]
    rubricRefs: Optional[List[str]] = None
    description: Optional[str] = None
    estimatedDurationMinutes: Optional[int] = None
