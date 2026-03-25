from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal


class PromptTextPart(BaseModel):
    type: Literal["text"]
    text: str


class PromptMathPart(BaseModel):
    type: Literal["math"]
    format: Literal["latex"] = "latex"
    source: str
    display: Optional[Literal["inline", "block"]] = "inline"
    altText: str


PromptPart = Union[PromptTextPart, PromptMathPart]

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
    promptParts: Optional[List[PromptPart]] = None

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
