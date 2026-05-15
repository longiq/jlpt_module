from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, computed_field


# ---------------------------------------------------------------------------
# Question schemas
# ---------------------------------------------------------------------------

class QuestionBase(BaseModel):
    level: str
    question_type: str
    passage: Optional[str] = None
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str           # "A" | "B" | "C" | "D"
    explanation: Optional[str] = None
    source_url: Optional[str] = None
    audio_url: Optional[str] = None


class QuestionCreate(QuestionBase):
    """Schema for creating a new question — identical to QuestionBase."""
    pass


class QuestionOut(QuestionBase):
    """Full question representation returned from the API (correct_answer visible)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime

    @computed_field
    @property
    def options(self) -> dict[str, str]:
        return {
            "A": self.option_a,
            "B": self.option_b,
            "C": self.option_c,
            "D": self.option_d,
        }


class QuestionForQuiz(BaseModel):
    """Question as seen by a quiz taker — correct_answer is intentionally omitted."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    level: str
    question_type: str
    passage: Optional[str] = None
    question_text: str
    options: dict[str, str]       # {"A": "...", "B": "...", "C": "...", "D": "..."} — already shuffled
    audio_url: Optional[str] = None


# ---------------------------------------------------------------------------
# Quiz session schemas
# ---------------------------------------------------------------------------

class QuizSessionCreate(BaseModel):
    level: str
    question_type: Optional[str] = None   # None means all types
    num_questions: int = 10
    full_exam: bool = False               # True = use real JLPT question counts


class QuizSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    level: str
    question_type: Optional[str] = None
    num_questions: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    score: Optional[float] = None
    total_questions: int
    correct_count: int


# ---------------------------------------------------------------------------
# Quiz answer / result schemas
# ---------------------------------------------------------------------------

class QuizAnswerSubmit(BaseModel):
    question_id: int
    user_answer: str              # "A" | "B" | "C" | "D"
    time_taken: Optional[float] = None


class QuizResultItem(BaseModel):
    question_id: int
    question_text: str
    user_answer: Optional[str]
    correct_answer: str           # shuffled-correct label (what the user sees)
    is_correct: Optional[bool]
    explanation: Optional[str] = None


class QuizResult(BaseModel):
    session_id: int
    level: str
    question_type: Optional[str]
    score: float                  # 0 – 100
    correct_count: int
    total_questions: int
    time_summary: dict[str, Any]
    answers: list[QuizResultItem]


# ---------------------------------------------------------------------------
# Session start response
# ---------------------------------------------------------------------------

class QuizStartResponse(BaseModel):
    session_id: int
    questions: list[QuestionForQuiz]
    total_minutes: Optional[int] = None   # set when full_exam=True
