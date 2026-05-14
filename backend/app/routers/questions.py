from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Question
from ..schemas import QuestionCreate, QuestionOut

router = APIRouter(tags=["questions"])


# ---------------------------------------------------------------------------
# GET /questions/stats/summary  — declared BEFORE /{question_id} to avoid
# the literal "stats" being matched as an integer path parameter.
# ---------------------------------------------------------------------------

@router.get("/stats/summary")
def question_stats(db: Session = Depends(get_db)):
    """Return total question count broken down by JLPT level and question type."""
    total = db.query(func.count(Question.id)).scalar()

    level_rows = (
        db.query(Question.level, func.count(Question.id))
        .group_by(Question.level)
        .all()
    )
    by_level: dict[str, int] = {row[0]: row[1] for row in level_rows}
    # Ensure all JLPT levels appear even when count is 0
    for lvl in ("N1", "N2", "N3", "N4", "N5"):
        by_level.setdefault(lvl, 0)

    type_rows = (
        db.query(Question.question_type, func.count(Question.id))
        .group_by(Question.question_type)
        .all()
    )
    by_type: dict[str, int] = {row[0]: row[1] for row in type_rows}
    for qt in ("vocabulary", "grammar", "reading", "listening"):
        by_type.setdefault(qt, 0)

    return {
        "total": total,
        "by_level": by_level,
        "by_type": by_type,
    }


# ---------------------------------------------------------------------------
# GET /questions  — list with optional filters
# ---------------------------------------------------------------------------

@router.get("/", response_model=list[QuestionOut])
def list_questions(
    level: Optional[str] = None,
    question_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List questions with optional filtering by level and/or question type."""
    query = db.query(Question)
    if level:
        query = query.filter(Question.level == level)
    if question_type:
        query = query.filter(Question.question_type == question_type)
    return query.offset(skip).limit(limit).all()


# ---------------------------------------------------------------------------
# GET /questions/{question_id}
# ---------------------------------------------------------------------------

@router.get("/{question_id}", response_model=QuestionOut)
def get_question(question_id: int, db: Session = Depends(get_db)):
    """Retrieve a single question by its ID (correct_answer is visible)."""
    question = db.get(Question, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question {question_id} not found.",
        )
    return question


# ---------------------------------------------------------------------------
# POST /questions
# ---------------------------------------------------------------------------

@router.post("/", response_model=QuestionOut, status_code=status.HTTP_201_CREATED)
def create_question(payload: QuestionCreate, db: Session = Depends(get_db)):
    """Create a new question and persist it to the database."""
    question = Question(**payload.model_dump())
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


# ---------------------------------------------------------------------------
# DELETE /questions/{question_id}
# ---------------------------------------------------------------------------

@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(question_id: int, db: Session = Depends(get_db)):
    """Delete a question by its ID."""
    question = db.get(Question, question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question {question_id} not found.",
        )
    db.delete(question)
    db.commit()
