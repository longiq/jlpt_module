from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Question

router = APIRouter(tags=["crawler"])


class CrawlRequest(BaseModel):
    level: str
    question_type: Optional[str] = None
    max_pages: int = 3
    source: str = "dethitiengnhat"  # "dethitiengnhat" | "lophoctiengnhat"


class CrawlResponse(BaseModel):
    added: int
    skipped: int
    errors: list[str] = []


class SeedResponse(BaseModel):
    added: int
    message: str


@router.post("/run", response_model=CrawlResponse)
def run_crawler(payload: CrawlRequest, db: Session = Depends(get_db)):
    """Trigger a web crawl for JLPT questions. Source: dethitiengnhat | lophoctiengnhat."""
    try:
        if payload.source == "lophoctiengnhat":
            from backend.crawler.lophoctiengnhat import LophoctiengnhatCrawler
            crawler = LophoctiengnhatCrawler()
        else:
            from backend.crawler.dethitiengnhat import DethitiengnhatCrawler
            crawler = DethitiengnhatCrawler()
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Crawler module not available.",
        )
    question_types = (
        [payload.question_type]
        if payload.question_type
        else ["vocabulary", "grammar", "reading"]
    )

    added = 0
    skipped = 0
    errors: list[str] = []

    for qtype in question_types:
        try:
            raw_questions = crawler.crawl(payload.level, qtype, max_pages=payload.max_pages)
        except Exception as e:
            errors.append(f"{qtype}: {str(e)}")
            continue

        for q in raw_questions:
            # Skip if all required fields are missing
            if not q.get("question_text") or not q.get("option_a"):
                skipped += 1
                continue

            # Deduplicate by question_text + level
            exists = (
                db.query(Question)
                .filter(
                    Question.level == payload.level,
                    Question.question_text == q["question_text"],
                )
                .first()
            )
            if exists:
                skipped += 1
                continue

            db.add(Question(
                level=payload.level,
                question_type=qtype,
                question_text=q.get("question_text", ""),
                passage=q.get("passage"),
                option_a=q.get("option_a", ""),
                option_b=q.get("option_b", ""),
                option_c=q.get("option_c", ""),
                option_d=q.get("option_d", ""),
                correct_answer=q.get("correct_answer", "A"),
                explanation=q.get("explanation"),
                source_url=q.get("source_url"),
                audio_url=q.get("audio_url"),
            ))
            added += 1

    if added:
        db.commit()

    return CrawlResponse(added=added, skipped=skipped, errors=errors)


@router.post("/seed", response_model=SeedResponse)
def load_seed_data(db: Session = Depends(get_db)):
    """Load built-in sample questions into the database."""
    try:
        from backend.crawler.seed_data import get_seed_questions
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Seed data module not available.",
        )

    questions = get_seed_questions()
    added = 0

    for q in questions:
        exists = (
            db.query(Question)
            .filter(
                Question.level == q["level"],
                Question.question_text == q["question_text"],
            )
            .first()
        )
        if exists:
            continue

        db.add(Question(**q))
        added += 1

    if added:
        db.commit()

    return SeedResponse(
        added=added,
        message=f"{added} 問追加しました。" if added else "追加する問題はありませんでした（既存データと重複）。",
    )
