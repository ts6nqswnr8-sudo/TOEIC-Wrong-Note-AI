from enum import Enum
from typing import Dict, Any
from pydantic import BaseModel, Field, model_validator


class TestType(str, Enum):
    LC = "LC"
    RC = "RC"


class ChoiceLabel(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class AnalyzeRequest(BaseModel):
    test_type: TestType
    part: int = Field(ge=1, le=7, description="TOEIC part number (1-7)")
    question_text: str = Field(min_length=1, description="The test question text")
    choices: Dict[str, str] = Field(description="Dictionary of choices, e.g. {'A': 'word', 'B': 'words'}")
    correct_answer: ChoiceLabel
    user_answer: ChoiceLabel

    @model_validator(mode="after")
    def validate_answers_in_choices(self) -> 'AnalyzeRequest':
        if str(self.correct_answer.value) not in self.choices:
            raise ValueError("correct_answer must be one of the provided choices keys.")
        if str(self.user_answer.value) not in self.choices:
            raise ValueError("user_answer must be one of the provided choices keys.")
        return self

    @model_validator(mode="after")
    def validate_non_empty_strings(self) -> 'AnalyzeRequest':
        if not self.question_text.strip():
            raise ValueError("question_text cannot be empty or whitespace only.")
        return self
