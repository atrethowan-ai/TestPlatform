from pydantic import BaseModel, Field
from typing import List, Optional, Union

class Question(BaseModel):
    id: str
    type: str
    prompt: str
    mediaRef: Optional[str] = None
    choices: Optional[List[str]] = None
    answerKey: Optional[Union[str, List[str]]] = None
    distractors: Optional[List[str]] = None
    rubricRef: Optional[str] = None
    domain: Optional[str] = None

class Section(BaseModel):
    id: str
    title: str
    questions: List[Question]

class Quiz(BaseModel):
    id: str
    title: str
    ageGroup: str
    sections: List[Section]
    rubricRefs: Optional[List[str]] = None
