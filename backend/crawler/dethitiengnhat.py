"""
Crawler for dethitiengnhat.com — a Vietnamese site hosting JLPT practice quizzes.

The site structure is not publicly documented, so this crawler applies a cascade
of CSS selectors to locate question content.  If the site is unavailable or its
markup has changed, the crawler returns an empty list rather than crashing.
"""

from __future__ import annotations

import logging
from typing import Optional

from bs4 import BeautifulSoup, Tag

from .base import BaseCrawler

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SITE_BASE = "https://dethitiengnhat.com"

# Maps our internal question_type values to the URL path suffixes used on the site.
QUESTION_TYPE_PATHS: dict[str, str] = {
    "grammar": "ngu-phap",
    "vocabulary": "tu-vung",
    "reading": "doc-hieu",
}

# Ordered list of CSS selectors tried when looking for question containers.
# The crawler stops at the first selector that yields usable results.
QUESTION_SELECTORS = [
    ".question",
    ".quiz-question",
    ".quiz-item",
    "[class*='question']",
    "[class*='quiz']",
    ".entry-content li",
    "article li",
    "li",
]

# Selectors tried (in order) for individual answer choices inside a question block.
CHOICE_SELECTORS = [
    ".answer",
    ".choice",
    "[class*='answer']",
    "[class*='choice']",
    "[class*='option']",
    "li",
    "label",
]

# CSS class fragments that may mark the correct answer choice.
CORRECT_CLASS_FRAGMENTS = ["correct", "right", "true", "active", "selected"]

ANSWER_LABELS = ("A", "B", "C", "D")


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

def _clean(text: Optional[str]) -> str:
    """Strip and collapse internal whitespace in *text*."""
    if not text:
        return ""
    return " ".join(text.split())


def _has_correct_marker(tag: Tag) -> bool:
    """Return ``True`` if *tag* carries a CSS class hinting at a correct answer."""
    classes: list[str] = tag.get("class", [])
    class_str = " ".join(classes).lower()
    return any(fragment in class_str for fragment in CORRECT_CLASS_FRAGMENTS)


def _extract_choices(container: Tag) -> tuple[list[str], str]:
    """
    Try to extract up to four answer choices from *container*.

    Returns
    -------
    choices        list of choice texts (may have fewer than 4 elements)
    correct_answer ``"A"`` | ``"B"`` | ``"C"`` | ``"D"`` | ``""``
    """
    choices: list[str] = []
    correct_answer = ""

    for selector in CHOICE_SELECTORS:
        items = container.select(selector)
        if len(items) >= 2:
            for idx, item in enumerate(items[:4]):
                choices.append(_clean(item.get_text()))
                if not correct_answer and _has_correct_marker(item):
                    correct_answer = ANSWER_LABELS[idx]
            break

    return choices, correct_answer


def _parse_question_block(
    block: Tag,
    source_url: str,
    level: str,
    question_type: str,
) -> Optional[dict]:
    """
    Attempt to build a question dict from a single HTML *block*.

    Returns ``None`` when the block does not contain enough data to form a
    meaningful question.
    """
    # --- question text -------------------------------------------------------
    question_text = ""
    for q_sel in [".question-text", ".quiz-question-text", "p", "h3", "h4", "strong"]:
        candidate = block.select_one(q_sel)
        if candidate:
            question_text = _clean(candidate.get_text())
            if question_text:
                break

    if not question_text:
        question_text = _clean(block.get_text())

    if not question_text:
        return None

    # --- choices -------------------------------------------------------------
    choices, correct_answer = _extract_choices(block)

    # Pad to exactly 4 entries so callers can safely unpack.
    while len(choices) < 4:
        choices.append("")

    option_a, option_b, option_c, option_d = choices[:4]

    # --- explanation ---------------------------------------------------------
    explanation = ""
    for ex_sel in [".explanation", ".answer-explanation", "[class*='explain']"]:
        ex_tag = block.select_one(ex_sel)
        if ex_tag:
            explanation = _clean(ex_tag.get_text())
            break

    # --- passage (reading questions only) ------------------------------------
    passage = ""
    if question_type == "reading":
        for p_sel in [
            ".passage",
            ".reading-text",
            "[class*='passage']",
            "[class*='reading']",
            "blockquote",
        ]:
            p_tag = block.select_one(p_sel)
            if p_tag:
                passage = _clean(p_tag.get_text())
                break

    return {
        "level": level,
        "question_type": question_type,
        "question_text": question_text,
        "option_a": option_a,
        "option_b": option_b,
        "option_c": option_c,
        "option_d": option_d,
        "correct_answer": correct_answer,
        "explanation": explanation,
        "source_url": source_url,
        "passage": passage,
    }


def _parse_page(
    soup: BeautifulSoup,
    source_url: str,
    level: str,
    question_type: str,
) -> list[dict]:
    """
    Extract all question dicts from a parsed HTML page.

    Iterates through ``QUESTION_SELECTORS`` and uses the first that produces
    at least one valid question dict.
    """
    questions: list[dict] = []

    for selector in QUESTION_SELECTORS:
        blocks = soup.select(selector)
        if not blocks:
            continue

        print(f"[dethitiengnhat] trying selector '{selector}' — found {len(blocks)} block(s)")

        for block in blocks:
            result = _parse_question_block(block, source_url, level, question_type)
            if result:
                questions.append(result)

        if questions:
            print(
                f"[dethitiengnhat] parsed {len(questions)} question(s) "
                f"with selector '{selector}'"
            )
            break
        else:
            print(
                f"[dethitiengnhat] selector '{selector}' matched blocks but none "
                f"yielded valid questions; trying next selector"
            )

    return questions


# ---------------------------------------------------------------------------
# Main crawler class
# ---------------------------------------------------------------------------

class DethitiengnhatCrawler(BaseCrawler):
    """Crawler targeting https://dethitiengnhat.com."""

    def __init__(self, delay: float = 2.0) -> None:
        super().__init__(base_url=SITE_BASE, delay=delay)

    # ------------------------------------------------------------------
    # URL construction
    # ------------------------------------------------------------------

    def _build_url(self, level: str, question_type: str, page: int) -> str:
        """Return the paginated URL for *level* / *question_type* / *page*."""
        level_path = level.lower()  # e.g. "n3"
        type_suffix = QUESTION_TYPE_PATHS.get(question_type, "")

        if type_suffix:
            base = f"{self.base_url}/{level_path}/{type_suffix}"
        else:
            # Unknown type — fall back to the level root page.
            base = f"{self.base_url}/{level_path}"

        if page > 1:
            return f"{base}?page={page}"
        return base

    # ------------------------------------------------------------------
    # Core crawl logic
    # ------------------------------------------------------------------

    def crawl(self, level: str, question_type: str, max_pages: int = 5) -> list[dict]:
        """
        Crawl dethitiengnhat.com and return question dicts.

        Args:
            level:         JLPT level, e.g. ``"N3"``.
            question_type: ``"vocabulary"`` | ``"grammar"`` | ``"reading"``.
            max_pages:     Maximum number of paginated pages to visit.

        Returns:
            List of question dicts (may be empty if the site is unreachable
            or the markup has changed beyond what the selectors handle).
        """
        all_questions: list[dict] = []
        seen_texts: set[str] = set()

        print(
            f"[dethitiengnhat] starting crawl — "
            f"level={level}, type={question_type}, max_pages={max_pages}"
        )

        for page in range(1, max_pages + 1):
            url = self._build_url(level, question_type, page)
            print(f"[dethitiengnhat] fetching page {page}: {url}")

            soup = self.fetch(url)
            if soup is None:
                print(f"[dethitiengnhat] fetch failed for {url}; stopping pagination")
                break

            page_questions = _parse_page(soup, url, level, question_type)

            if not page_questions:
                print(
                    f"[dethitiengnhat] no questions found on page {page}; "
                    f"stopping pagination"
                )
                break

            # Deduplicate across pages by question stem text.
            new_count = 0
            for q in page_questions:
                key = q["question_text"]
                if key not in seen_texts:
                    seen_texts.add(key)
                    all_questions.append(q)
                    new_count += 1

            print(
                f"[dethitiengnhat] page {page}: {new_count} new question(s) added "
                f"(running total: {len(all_questions)})"
            )

            if new_count == 0:
                print("[dethitiengnhat] no new questions on this page; stopping pagination")
                break

        print(f"[dethitiengnhat] crawl complete — {len(all_questions)} question(s) returned")
        return all_questions
