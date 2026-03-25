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

class Question(BaseModel):
    id: str
    type: str
    prompt: str
    subcategory: str
    skill: str
    mediaRef: Optional[str] = None
    choices: Optional[List[str]] = None
    answerKey: Optional[Union[str, List[str]]] = None
    distractors: Optional[List[str]] = None
    rubricRef: Optional[str] = None
    domain: Optional[str] = None
    promptParts: Optional[List[PromptPart]] = None

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
