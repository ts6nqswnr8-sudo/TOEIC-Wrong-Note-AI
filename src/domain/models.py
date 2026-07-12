from enum import Enum
from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field, model_validator, ConfigDict
from pydantic.alias_generators import to_camel


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


# --- TASK-101 구현부 ---

class ErrorCategoryCode(str, Enum):
    PART_OF_SPEECH = "PART_OF_SPEECH"
    TENSE_VOICE = "TENSE_VOICE"
    AGREEMENT_PRONOUN = "AGREEMENT_PRONOUN"
    CONNECTOR = "CONNECTOR"
    SENTENCE_STRUCTURE = "SENTENCE_STRUCTURE"
    VOCABULARY = "VOCABULARY"
    PREPOSITION_IDIOM = "PREPOSITION_IDIOM"
    EVIDENCE_FINDING = "EVIDENCE_FINDING"
    PARAPHRASING = "PARAPHRASING"
    LISTENING = "LISTENING"
    CARELESS_MISTAKE = "CARELESS_MISTAKE"
    OTHER = "OTHER"


class PartOfSpeech(str, Enum):
    noun = "noun"
    verb = "verb"
    adjective = "adjective"
    adverb = "adverb"
    preposition = "preposition"
    conjunction = "conjunction"
    phrase = "phrase"


class WrongNoteBaseModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel
    )

    @model_validator(mode="after")
    def validate_strings_not_empty(self) -> 'WrongNoteBaseModel':
        # 필드를 객체 루프로 돌면서 문자열이 존재할 경우 공백(whitespaces/empty) 문자열 검증
        for field_name, value in self:
            if isinstance(value, str):
                if not value.strip():
                    raise ValueError(f"{field_name} cannot be empty or whitespace only.")
        return self


class TranslationChoices(WrongNoteBaseModel):
    A: str
    B: str
    C: str
    D: str


class Translation(WrongNoteBaseModel):
    question: str
    choices: TranslationChoices


class CorrectAnswer(WrongNoteBaseModel):
    choice: ChoiceLabel
    text: str


class CorrectReason(WrongNoteBaseModel):
    summary: str = Field(max_length=30)
    detail: str
    grammar_rule: Optional[str] = None


class WrongAnswerReason(WrongNoteBaseModel):
    selected_choice: ChoiceLabel
    selected_text: str
    summary: str = Field(max_length=30)
    detail: str


class ErrorCategory(WrongNoteBaseModel):
    primary: ErrorCategoryCode
    secondary: Optional[ErrorCategoryCode] = None
    description: str


class LearningPointExample(WrongNoteBaseModel):
    english: str
    korean: str


class LearningPoint(WrongNoteBaseModel):
    title: str
    explanation: str
    examples: List[LearningPointExample] = Field(min_length=2, max_length=3)
    tip: str


class VocabularyItem(WrongNoteBaseModel):
    word: str
    part_of_speech: PartOfSpeech
    meaning: str
    example_sentence: str


class Confidence(WrongNoteBaseModel):
    score: float = Field(ge=0.0, le=1.0)
    reason: str


class AnalysisResult(WrongNoteBaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")
    part: Optional[int] = None
    translation: Translation
    correct_answer: CorrectAnswer
    correct_reason: CorrectReason
    wrong_answer_reason: WrongAnswerReason
    error_category: ErrorCategory
    learning_point: LearningPoint
    vocabulary: List[VocabularyItem] = Field(min_length=1, max_length=5)
    confidence: Confidence
    disclaimer: str = "이 분석은 AI가 생성한 것으로, 실제 출제 의도와 다를 수 있습니다. 참고 자료로 활용하시고, 정확한 해설은 공식 교재를 확인하세요."
