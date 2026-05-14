"""
Crawler for lophoctiengnhat.com — a Vietnamese site hosting JLPT practice quizzes.

Uses browser-like headers to bypass basic bot detection.  Returns an empty list
rather than raising when the site is unreachable or its markup has changed.
"""

from __future__ import annotations

import logging
from typing import Optional

from bs4 import BeautifulSoup, Tag

from .base import BaseCrawler

logger = logging.getLogger(__name__)

SITE_BASE = "https://lophoctiengnhat.com"

# URL path suffixes per question type
QUESTION_TYPE_PATHS: dict[str, list[str]] = {
    "vocabulary": ["tu-vung", "bai-tap-tu-vung"],
    "grammar":    ["ngu-phap", "bai-tap-ngu-phap"],
    "reading":    ["doc-hieu", "bai-tap-doc-hieu"],
}

# CSS selectors tried in order for question containers
QUESTION_SELECTORS = [
    ".question",
    ".quiz-question",
    ".bai-tap",
    "[class*='question']",
    "[class*='quiz']",
    "[class*='bai-tap']",
    ".entry-content > ol > li",
    ".entry-content > ul > li",
    "article li",
    "li",
]

# CSS selectors tried for answer choices inside a question block
CHOICE_SELECTORS = [
    ".answer",
    ".choice",
    ".dap-an",
    "[class*='answer']",
    "[class*='choice']",
    "[class*='dap-an']",
    "[class*='option']",
    "li",
    "label",
]

CORRECT_CLASS_FRAGMENTS = ["correct", "right", "true", "active", "dung", "correct-answer"]

ANSWER_LABELS = ("A", "B", "C", "D")


def _clean(text: Optional[str]) -> str:
    if not text:
        return ""
    return " ".join(text.split())


def _has_correct_marker(tag: Tag) -> bool:
    classes = " ".join(tag.get("class", [])).lower()
    return any(f in classes for f in CORRECT_CLASS_FRAGMENTS)


def _extract_choices(container: Tag) -> tuple[list[str], str]:
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


def _parse_question_block(block: Tag, source_url: str, level: str, question_type: str) -> Optional[dict]:
    question_text = ""
    for sel in [".question-text", ".cau-hoi", "p", "h3", "h4", "strong"]:
        candidate = block.select_one(sel)
        if candidate:
            question_text = _clean(candidate.get_text())
            if question_text:
                break
    if not question_text:
        question_text = _clean(block.get_text())
    if not question_text:
        return None

    choices, correct_answer = _extract_choices(block)
    while len(choices) < 4:
        choices.append("")
    option_a, option_b, option_c, option_d = choices[:4]

    explanation = ""
    for sel in [".explanation", ".giai-thich", "[class*='explain']", "[class*='giai']"]:
        ex = block.select_one(sel)
        if ex:
            explanation = _clean(ex.get_text())
            break

    passage = ""
    if question_type == "reading":
        for sel in [".passage", ".doan-van", "blockquote", "[class*='passage']"]:
            p = block.select_one(sel)
            if p:
                passage = _clean(p.get_text())
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


def _parse_page(soup: BeautifulSoup, source_url: str, level: str, question_type: str) -> list[dict]:
    questions: list[dict] = []
    for selector in QUESTION_SELECTORS:
        blocks = soup.select(selector)
        if not blocks:
            continue
        print(f"[lophoctiengnhat] selector '{selector}' — {len(blocks)} block(s)")
        for block in blocks:
            result = _parse_question_block(block, source_url, level, question_type)
            if result:
                questions.append(result)
        if questions:
            print(f"[lophoctiengnhat] parsed {len(questions)} question(s) with selector '{selector}'")
            break
    return questions


class LophoctiengnhatCrawler(BaseCrawler):
    """Crawler targeting https://lophoctiengnhat.com."""

    def __init__(self, delay: float = 2.0) -> None:
        super().__init__(base_url=SITE_BASE, delay=delay)

    def _build_urls(self, level: str, question_type: str, page: int) -> list[str]:
        level_path = level.lower()
        suffixes = QUESTION_TYPE_PATHS.get(question_type, [""])
        urls = []
        for suffix in suffixes:
            base = f"{self.base_url}/{level_path}/{suffix}" if suffix else f"{self.base_url}/{level_path}"
            urls.append(f"{base}?page={page}" if page > 1 else base)
        return urls

    def crawl(self, level: str, question_type: str, max_pages: int = 5) -> list[dict]:
        all_questions: list[dict] = []
        seen_texts: set[str] = set()

        print(f"[lophoctiengnhat] crawl start — level={level}, type={question_type}, max_pages={max_pages}")

        for page in range(1, max_pages + 1):
            page_questions: list[dict] = []
            urls = self._build_urls(level, question_type, page)

            for url in urls:
                print(f"[lophoctiengnhat] fetching: {url}")
                soup = self.fetch(url)
                if soup is None:
                    print(f"[lophoctiengnhat] fetch failed: {url}")
                    continue
                parsed = _parse_page(soup, url, level, question_type)
                page_questions.extend(parsed)
                if parsed:
                    break  # stop trying alternate URL paths once one works

            if not page_questions:
                print(f"[lophoctiengnhat] no questions on page {page}; stopping")
                break

            new_count = 0
            for q in page_questions:
                if q["question_text"] not in seen_texts:
                    seen_texts.add(q["question_text"])
                    all_questions.append(q)
                    new_count += 1

            print(f"[lophoctiengnhat] page {page}: {new_count} new (total: {len(all_questions)})")
            if new_count == 0:
                break

        print(f"[lophoctiengnhat] done — {len(all_questions)} question(s)")
        return all_questions
