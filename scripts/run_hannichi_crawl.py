"""
Standalone script to run the HanNichiCrawler and optionally save results to the DB.

Usage examples:
  # Dry-run: show results without touching DB
  python scripts/run_hannichi_crawl.py --level N5 --type vocabulary --dry-run

  # Crawl all types for N4, save to DB
  python scripts/run_hannichi_crawl.py --level N4 --save-to-db

  # Crawl all levels and all types, write JSON output
  python scripts/run_hannichi_crawl.py --level all --output data/hannichi_all.json

  # Custom credentials
  python scripts/run_hannichi_crawl.py --level N3 --username myuser --password mypass --dry-run
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# Ensure the project root is on sys.path so backend imports work.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("run_hannichi_crawl")

LEVELS = ["N5", "N4", "N3", "N2", "N1"]
QUESTION_TYPES = ["vocabulary", "grammar", "reading"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Crawl han-nichi.vercel.app and optionally import to the JLPT DB."
    )
    p.add_argument(
        "--level",
        default="N5",
        help="JLPT level to crawl: N5 | N4 | N3 | N2 | N1 | all  (default: N5)",
    )
    p.add_argument(
        "--type",
        dest="question_type",
        default=None,
        help="Question type: vocabulary | grammar | reading | all  (default: all)",
    )
    p.add_argument(
        "--max-pages",
        type=int,
        default=5,
        help="Maximum paginated pages per (level, type) combination (default: 5)",
    )
    p.add_argument(
        "--username",
        default="duyhai",
        help="Login username (default: duyhai)",
    )
    p.add_argument(
        "--password",
        default="Abc12345",
        help="Login password",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print questions to stdout without writing to the database",
    )
    p.add_argument(
        "--save-to-db",
        action="store_true",
        help="Import crawled questions into the SQLite database",
    )
    p.add_argument(
        "--output",
        default=None,
        help="Write results as JSON to this file path",
    )
    return p.parse_args()


def crawl_all(args: argparse.Namespace) -> list[dict]:
    from backend.crawler.hannichi import HanNichiCrawler

    crawler = HanNichiCrawler(
        username=args.username,
        password=args.password,
    )

    levels = LEVELS if args.level.lower() == "all" else [args.level.upper()]
    types = (
        QUESTION_TYPES
        if args.question_type is None or args.question_type.lower() == "all"
        else [args.question_type]
    )

    all_questions: list[dict] = []

    for level in levels:
        for qtype in types:
            logger.info("--- Crawling level=%s type=%s ---", level, qtype)
            questions = crawler.crawl(level, qtype, max_pages=args.max_pages)
            logger.info("  → %d questions collected", len(questions))
            all_questions.extend(questions)

    return all_questions


def save_to_db(questions: list[dict]) -> tuple[int, int]:
    """Insert questions into the SQLite DB; return (added, skipped) counts."""
    from backend.app.database import SessionLocal
    from backend.app.models import Question

    db = SessionLocal()
    added = skipped = 0
    try:
        for q in questions:
            if not q.get("question_text") or not q.get("option_a"):
                skipped += 1
                continue
            exists = (
                db.query(Question)
                .filter(
                    Question.level == q["level"],
                    Question.question_text == q["question_text"],
                )
                .first()
            )
            if exists:
                skipped += 1
                continue
            db.add(Question(
                level=q["level"],
                question_type=q["question_type"],
                question_text=q["question_text"],
                passage=q.get("passage") or "",
                option_a=q.get("option_a", ""),
                option_b=q.get("option_b", ""),
                option_c=q.get("option_c", ""),
                option_d=q.get("option_d", ""),
                correct_answer=q.get("correct_answer", "A"),
                explanation=q.get("explanation") or "",
                source_url=q.get("source_url") or "",
            ))
            added += 1
        if added:
            db.commit()
    finally:
        db.close()
    return added, skipped


def main() -> None:
    args = parse_args()

    questions = crawl_all(args)
    logger.info("Total questions collected: %d", len(questions))

    if not questions:
        logger.warning("No questions collected. Check logs for authentication or endpoint errors.")
        sys.exit(1)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(questions, ensure_ascii=False, indent=2))
        logger.info("Results written to %s", out_path)

    if args.dry_run:
        print(json.dumps(questions, ensure_ascii=False, indent=2))
        logger.info("Dry-run mode — database not modified.")
        return

    if args.save_to_db:
        added, skipped = save_to_db(questions)
        logger.info("DB import complete: added=%d skipped=%d", added, skipped)
    else:
        logger.info(
            "Use --dry-run to preview or --save-to-db to import into the database."
        )
        print(json.dumps(questions[:5], ensure_ascii=False, indent=2))
        if len(questions) > 5:
            logger.info("(showing first 5 of %d; use --output to save all)", len(questions))


if __name__ == "__main__":
    main()
