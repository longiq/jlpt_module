from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    level = Column(String, nullable=False, index=True)           # "N1" | "N2" | "N3" | "N4" | "N5"
    question_type = Column(String, nullable=False, index=True)   # "vocabulary" | "grammar" | "reading" | "listening"
    passage = Column(Text, nullable=True)                        # shared reading passage (optional)
    question_text = Column(Text, nullable=False)
    option_a = Column(String, nullable=False)
    option_b = Column(String, nullable=False)
    option_c = Column(String, nullable=False)
    option_d = Column(String, nullable=False)
    correct_answer = Column(String, nullable=False)              # "A" | "B" | "C" | "D"
    explanation = Column(Text, nullable=True)
    source_url = Column(String, nullable=True)
    audio_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    quiz_answers = relationship("QuizAnswer", back_populates="question")


class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    level = Column(String, nullable=False)
    question_type = Column(String, nullable=True)    # None means all types
    num_questions = Column(Integer, default=10, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    score = Column(Float, nullable=True)             # 0 – 100
    total_questions = Column(Integer, nullable=False)
    correct_count = Column(Integer, default=0, nullable=False)
    # JSON array of question ids in the order they were presented to the user
    session_questions = Column(Text, nullable=True)

    answers = relationship(
        "QuizAnswer",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class QuizAnswer(Base):
    __tablename__ = "quiz_answers"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    session_id = Column(Integer, ForeignKey("quiz_sessions.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    user_answer = Column(String, nullable=True)       # "A"/"B"/"C"/"D" — null until submitted
    is_correct = Column(Boolean, nullable=True)
    time_taken = Column(Float, nullable=True)         # seconds spent on this question
    answered_at = Column(DateTime, nullable=True)
    # Correct answer label AFTER shuffling (may differ from Question.correct_answer)
    shuffled_correct = Column(String, nullable=True)

    session = relationship("QuizSession", back_populates="answers")
    question = relationship("Question", back_populates="quiz_answers")
