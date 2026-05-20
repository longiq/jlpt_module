"""
Standalone script to run the HanNichiCrawler and optionally save results to the DB.

The site backend (Supabase Storage) may be blocked from cloud environments.
Run this script on your LOCAL machine where your IP is allowed.

Usage examples:
  # Dry-run: show results without touching DB
  python scripts/run_hannichi_crawl.py --level N5 --dry-run

  # Use pre-obtained Bearer token (copy from browser DevTools → Network → Authorization header)
  python scripts/run_hannichi_crawl.py --level N2 --token "eyJhbGci..." --dry-run

  # List all files in the Supabase bucket
  python scripts/run_hannichi_crawl.py --list-files --token "eyJhbGci..."

  # Crawl all levels and all types, save to DB
  python scripts/run_hannichi_crawl.py --level all --save-to-db

  # Write JSON output
  python scripts/run_hannichi_crawl.py --level N2 --output data/hannichi_n2.json --token "eyJhbGci..."
"""

import argparse
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("run_hannichi_crawl")

LEVELS = ["N5", "N4", "N3", "N2", "N1"]
QUESTION_TYPES = ["vocabulary", "grammar", "reading", "listening"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Crawl han-nichi.vercel.app (Supabase Storage) and optionally import to JLPT DB."
    )
    p.add_argument("--level", default="N5",
        help="JLPT level: N5|N4|N3|N2|N1|all  (default: N5)")
    p.add_argument("--type", dest="question_type", default=None,
        help="Question type: vocabulary|grammar|reading|listening|all  (default: all)")
    p.add_argument("--max-files", type=int, default=10,
        help="Max exam files to download per (level, type) combo (default: 10)")
    p.add_argument("--username", default="duyhai",
        help="Login username/email (default: duyhai)")
    p.add_argument("--password", default="Abc12345",
        help="Login password")
    p.add_argument("--token", default=None,
        help="Bearer token from browser DevTools (bypasses login step)")
    p.add_argument("--dry-run", action="store_true",
        help="Print first 5 questions to stdout without writing to DB")
    p.add_argument("--save-to-db", action="store_true",
        help="Import crawled questions into the SQLite database")
    p.add_argument("--output", default=None,
        help="Write all results as JSON to this file path")
    p.add_argument("--list-files", action="store_true",
        help="List all files in the Supabase 'jlpt' bucket and exit")
    p.add_argument("--verbose", action="store_true",
        help="Enable DEBUG logging")
    return p.parse_args()


def make_crawler(args: argparse.Namespace):
    from backend.crawler.hannichi import HanNichiCrawler
    return HanNichiCrawler(
        username=args.username,
        password=args.password,
        token=args.token,
    )


def do_list_files(args: argparse.Namespace) -> None:
    crawler = make_crawler(args)
    if not crawler._authenticated and not crawler.authenticate():
        logger.error("Authentication failed — cannot list files")
        sys.exit(1)
    files = crawler._list_bucket()
    if files:
        print(f"\nFiles in 'jlpt' bucket ({len(files)} total):")
        for f in sorted(files):
            print(" ", f)
    else:
        print("No files found or bucket listing failed.")


def crawl_all(args: argparse.Namespace) -> list[dict]:
    crawler = make_crawler(args)

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
            questions = crawler.crawl(level, qtype, max_pages=args.max_files)
            logger.info("  → %d questions collected", len(questions))
            all_questions.extend(questions)

    return all_questions


def save_to_db(questions: list[dict]) -> tuple[int, int]:
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
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.list_files:
        do_list_files(args)
        return

    questions = crawl_all(args)
    logger.info("Total questions collected: %d", len(questions))

    if not questions:
        logger.warning(
            "No questions collected.\n"
            "  → Make sure you're running this on a machine where han-nichi.vercel.app is accessible.\n"
            "  → Or supply --token with a Bearer token from your browser's DevTools."
        )
        sys.exit(1)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(questions, ensure_ascii=False, indent=2))
        logger.info("Results written to %s", out_path)

    if args.dry_run:
        print(json.dumps(questions[:5], ensure_ascii=False, indent=2))
        if len(questions) > 5:
            logger.info("(showing first 5 of %d; use --output to save all)", len(questions))
        logger.info("Dry-run — database not modified.")
        return

    if args.save_to_db:
        added, skipped = save_to_db(questions)
        logger.info("DB import complete: added=%d  skipped=%d", added, skipped)
    else:
        logger.info("Use --dry-run to preview or --save-to-db to import into the DB.")
        print(json.dumps(questions[:5], ensure_ascii=False, indent=2))
        if len(questions) > 5:
            logger.info("(showing first 5 of %d; use --output to save all)", len(questions))


if __name__ == "__main__":
    main()
