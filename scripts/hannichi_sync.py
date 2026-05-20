"""
End-to-end pipeline: han-nichi.vercel.app PDF → AI answers → SQLite DB.

Usage examples:

    # Dry run (print results, no DB write)
    python scripts/hannichi_sync.py --dry-run

    # Download all levels and import
    python scripts/hannichi_sync.py --save-to-db

    # Single level
    python scripts/hannichi_sync.py --level N2 --save-to-db

    # Re-parse existing PDFs (skip Playwright download step)
    python scripts/hannichi_sync.py --pdf-dir data/pdfs/ --level N2 --save-to-db

    # Use a proxy (also settable via PLAYWRIGHT_PROXY env var)
    PLAYWRIGHT_PROXY=socks5://user:pass@host:1080 python scripts/hannichi_sync.py --save-to-db

Environment:
    ANTHROPIC_API_KEY   Required for AI answer generation.
    PLAYWRIGHT_PROXY    Optional proxy URL for Playwright.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

# Allow running from repo root without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

JLPT_LEVELS = ["N1", "N2", "N3", "N4", "N5"]
DEFAULT_PDF_DIR = "data/pdfs"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Download JLPT PDFs from han-nichi, fill answers with AI, import to DB."
    )
    p.add_argument("--level", choices=JLPT_LEVELS, help="Only process this JLPT level.")
    p.add_argument("--pdf-dir", default=DEFAULT_PDF_DIR, help="Directory for PDF files.")
    p.add_argument("--save-to-db", action="store_true", help="Write questions to SQLite DB.")
    p.add_argument("--dry-run", action="store_true", help="Parse and AI-fill but do not write DB.")
    p.add_argument("--skip-download", action="store_true", help="Skip Playwright download; use existing PDFs in --pdf-dir.")
    p.add_argument("--skip-ai", action="store_true", help="Skip AI answer step (correct_answer will be empty).")
    p.add_argument("--headless", action="store_true", default=True, help="Run browser headless (default).")
    p.add_argument("--visible", action="store_true", help="Run browser with GUI (disables headless).")
    p.add_argument("--verbose", action="store_true", help="Debug logging.")
    return p.parse_args()


# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------

def step_download(args: argparse.Namespace) -> list[dict]:
    """Use PlaywrightCrawler to download PDFs; returns list of {pdf_path, level, ...}."""
    from backend.crawler.playwright_crawler import PlaywrightCrawler

    headless = not args.visible
    crawler = PlaywrightCrawler(headless=headless)
    return crawler.download_all_pdfs(output_dir=args.pdf_dir, level=args.level)


def step_collect_existing_pdfs(pdf_dir: str, level: str | None) -> list[dict]:
    """Scan --pdf-dir for existing PDFs and return metadata list."""
    base = Path(pdf_dir)
    if not base.exists():
        logger.warning("--pdf-dir '%s' does not exist", pdf_dir)
        return []

    results: list[dict] = []
    for pdf_file in sorted(base.glob("*.pdf")):
        # Expect filenames like N2-2024-7.pdf or N2-2024-7-1.pdf
        name = pdf_file.stem
        parts = name.split("-")
        detected_level = parts[0].upper() if parts and parts[0].upper() in JLPT_LEVELS else None
        if level and detected_level != level.upper():
            continue
        if not detected_level:
            # Can't determine level — include anyway and let parser fail gracefully
            detected_level = level or "N2"
        exam_id = "-".join(parts[1:]) if len(parts) > 1 else name
        results.append({
            "pdf_path": str(pdf_file),
            "level": detected_level,
            "exam_id": exam_id,
            "source_url": f"file://{pdf_file.resolve()}",
        })

    logger.info("Found %d existing PDF(s) in %s", len(results), pdf_dir)
    return results


def step_parse(pdf_infos: list[dict]) -> list[dict]:
    """Parse each PDF with PdfParser; return flat list of question dicts (no answers yet)."""
    from backend.crawler.pdf_parser import PdfParser

    parser = PdfParser()
    all_questions: list[dict] = []
    for info in pdf_infos:
        pdf_path = info["pdf_path"]
        level = info["level"]
        try:
            qs = parser.parse(pdf_path, level)
            logger.info("  %s → %d questions", Path(pdf_path).name, len(qs))
            all_questions.extend(qs)
        except Exception as exc:
            logger.error("  parse error %s: %s", pdf_path, exc)

    logger.info("Parsed total: %d questions", len(all_questions))
    return all_questions


def step_fill_answers(questions: list[dict]) -> list[dict]:
    """Call Claude API to fill correct_answer + explanation for every question."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error(
            "ANTHROPIC_API_KEY not set. Export it before running:\n"
            "  export ANTHROPIC_API_KEY=sk-ant-..."
        )
        sys.exit(1)

    from backend.crawler.ai_answerer import AIAnswerer

    answerer = AIAnswerer(api_key=api_key)
    logger.info("Filling answers for %d questions (batches of %d)...", len(questions), AIAnswerer.BATCH_SIZE)
    return answerer.fill_answers(questions)


def step_save_to_db(questions: list[dict]) -> tuple[int, int]:
    """Dedup and insert questions into the SQLite DB. Returns (added, skipped)."""
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
                question_type=q.get("question_type", "vocabulary"),
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
            logger.info("DB: +%d added, %d skipped", added, skipped)
    finally:
        db.close()
    return added, skipped


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not args.save_to_db and not args.dry_run:
        logger.error("Specify --save-to-db or --dry-run.")
        sys.exit(1)

    # ── Step 1: Obtain PDF metadata ──────────────────────────────────────
    if args.skip_download:
        logger.info("=== Step 1: Using existing PDFs in '%s' ===", args.pdf_dir)
        pdf_infos = step_collect_existing_pdfs(args.pdf_dir, args.level)
    else:
        logger.info("=== Step 1: Downloading PDFs via Playwright ===")
        pdf_infos = step_download(args)

    if not pdf_infos:
        logger.warning(
            "No PDFs found.\n"
            "  → If you're on a datacenter IP, han-nichi.vercel.app may block you.\n"
            "  → Set PLAYWRIGHT_PROXY to route through a residential/office IP.\n"
            "  → Or place existing PDFs in --pdf-dir and re-run with --skip-download."
        )
        sys.exit(1)

    logger.info("PDFs to process: %d", len(pdf_infos))

    # ── Step 2: Parse PDFs ───────────────────────────────────────────────
    logger.info("=== Step 2: Parsing PDFs ===")
    questions = step_parse(pdf_infos)

    if not questions:
        logger.error("No questions extracted from any PDF. Check PDF layout.")
        sys.exit(1)

    # ── Step 3: AI fill answers ──────────────────────────────────────────
    if not args.skip_ai:
        logger.info("=== Step 3: AI answer generation ===")
        questions = step_fill_answers(questions)
    else:
        logger.info("=== Step 3: Skipped (--skip-ai) ===")

    # ── Preview ──────────────────────────────────────────────────────────
    if args.dry_run or args.verbose:
        preview = questions[:3]
        logger.info("=== Preview (first %d questions) ===", len(preview))
        print(json.dumps(preview, ensure_ascii=False, indent=2))

    # ── Step 4: Save to DB ───────────────────────────────────────────────
    total_added = total_skipped = 0
    if args.save_to_db:
        logger.info("=== Step 4: Saving to DB ===")
        total_added, total_skipped = step_save_to_db(questions)
    else:
        logger.info("=== Step 4: Skipped (dry-run) ===")

    # ── Summary ──────────────────────────────────────────────────────────
    logger.info("━━━ Summary ━━━")
    logger.info("  PDFs processed : %d", len(pdf_infos))
    logger.info("  Questions found: %d", len(questions))
    if args.save_to_db:
        logger.info("  DB added       : %d", total_added)
        logger.info("  DB skipped     : %d", total_skipped)


if __name__ == "__main__":
    main()
