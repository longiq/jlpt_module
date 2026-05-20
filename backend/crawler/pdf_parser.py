"""
Parse JLPT exam PDFs exported from han-nichi.vercel.app.

A typical han-nichi PDF layout (N2, language knowledge section):

    問題1  ＿＿の言葉の読み方として最もよいものを、1・2・3・4から一つ選びなさい。

    1  このタオルはまだ（しめって）いる。
       1 渡って   2 温って   3 汗って   4 湿って

    2  ...

Reading sections include a passage before the numbered questions.

Output dicts have the same keys as the Question model except
correct_answer and explanation (those are filled by AIAnswerer).
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Section → question_type mapping per JLPT level (mirrors hannichi.py)
# ---------------------------------------------------------------------------
SECTION_TYPE_MAP: dict[str, list[tuple[int, str]]] = {
    "N1": [(4, "vocabulary"), (7, "grammar"),  (99, "reading")],
    "N2": [(6, "vocabulary"), (8, "grammar"),  (99, "reading")],
    "N3": [(8, "vocabulary"), (10, "grammar"), (99, "reading")],
    "N4": [(4, "vocabulary"), (8, "grammar"),  (99, "reading")],
    "N5": [(4, "vocabulary"), (7, "grammar"),  (99, "reading")],
}

# Patterns
_RE_SECTION = re.compile(r"問題\s*(\d+)", re.UNICODE)
_RE_QUESTION = re.compile(r"^\s*(\d{1,2})[．\.\s　](.+)", re.UNICODE)
_RE_OPTION_INLINE = re.compile(
    r"[1１]\s*([^\s　1-4１-４]{2,})\s*"
    r"[2２]\s*([^\s　1-4１-４]{2,})\s*"
    r"[3３]\s*([^\s　1-4１-４]{2,})\s*"
    r"[4４]\s*([^\s　1-4１-４]{2,})",
    re.UNICODE,
)
_RE_OPTION_START = re.compile(r"^\s*[1-4１-４][　\s](.+)", re.UNICODE)


def _clean(text: str) -> str:
    return " ".join((text or "").split())


def _section_type(level: str, sec_num: int) -> str:
    for max_sec, qtype in SECTION_TYPE_MAP.get(level.upper(), SECTION_TYPE_MAP["N2"]):
        if sec_num <= max_sec:
            return qtype
    return "reading"


# ---------------------------------------------------------------------------


class PdfParser:
    """Parse a JLPT exam PDF into Question dicts (without answers)."""

    def parse(self, pdf_path: str, level: str) -> list[dict]:
        """
        Extract questions from *pdf_path*.

        Returns a list of dicts with keys:
            level, question_type, question_text,
            option_a, option_b, option_c, option_d,
            passage, source_url
        (correct_answer and explanation are absent — filled by AIAnswerer)
        """
        try:
            import pdfplumber
        except ImportError:
            raise ImportError("pdfplumber is required: pip install pdfplumber")

        path = Path(pdf_path)
        level = level.upper()
        source_url = f"file://{path.resolve()}"

        with pdfplumber.open(str(path)) as pdf:
            pages_text = [page.extract_text() or "" for page in pdf.pages]

        full_text = "\n".join(pages_text)
        logger.info("[pdf_parser] %s — %d pages, %d chars", path.name, len(pages_text), len(full_text))

        questions = self._parse_text(full_text, level, source_url)
        logger.info("[pdf_parser] extracted %d questions from %s", len(questions), path.name)
        return questions

    # ------------------------------------------------------------------

    def _parse_text(self, text: str, level: str, source_url: str) -> list[dict]:
        lines = text.splitlines()
        questions: list[dict] = []

        current_sec_num = 0
        current_qtype = "vocabulary"
        current_passage: list[str] = []
        in_passage = False

        # State machine: collect lines, detect section/question boundaries
        q_buf: list[str] = []   # lines belonging to current question
        q_num: int | None = None

        def flush_question(buf: list[str], sec_num: int, qtype: str, passage: str) -> dict | None:
            return self._build_question(buf, level, qtype, passage, source_url)

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # ---- Section header ----
            sec_match = _RE_SECTION.search(stripped)
            if sec_match and len(stripped) < 120:
                if q_buf and q_num is not None:
                    q = flush_question(q_buf, current_sec_num, current_qtype, " ".join(current_passage))
                    if q:
                        questions.append(q)
                    q_buf, q_num = [], None

                new_sec_num = int(sec_match.group(1))
                if new_sec_num != current_sec_num:
                    current_sec_num = new_sec_num
                    current_qtype = _section_type(level, current_sec_num)
                    current_passage = []
                    in_passage = (current_qtype == "reading")
                    logger.debug("[pdf_parser] section %d → %s", current_sec_num, current_qtype)
                i += 1
                continue

            # ---- Question start ----
            q_match = _RE_QUESTION.match(line)
            if q_match and current_sec_num > 0:
                num = int(q_match.group(1))
                # Sanity: question numbers should be sequential-ish
                if num >= 1 and (q_num is None or num == q_num + 1 or num <= q_num + 3):
                    if q_buf and q_num is not None:
                        q = flush_question(q_buf, current_sec_num, current_qtype, " ".join(current_passage))
                        if q:
                            questions.append(q)
                    q_num = num
                    q_buf = [stripped]
                    in_passage = False
                    i += 1
                    continue

            # ---- Accumulate into question buffer or passage ----
            if q_num is not None:
                q_buf.append(stripped)
            elif in_passage and stripped:
                current_passage.append(stripped)

            i += 1

        # Flush last question
        if q_buf and q_num is not None:
            q = flush_question(q_buf, current_sec_num, current_qtype, " ".join(current_passage))
            if q:
                questions.append(q)

        return questions

    def _build_question(
        self,
        buf: list[str],
        level: str,
        qtype: str,
        passage: str,
        source_url: str,
    ) -> dict | None:
        if not buf:
            return None

        full = " ".join(buf)

        # Try to extract 4 options from the combined text
        opts = self._extract_options(full)
        if opts is None:
            # Try line-by-line option detection
            opts = self._extract_options_multiline(buf)

        if opts is None:
            logger.debug("[pdf_parser] no options found in: %s", full[:80])
            return None

        a, b, c, d = opts

        # Question text is everything before the first option marker
        q_text = self._extract_question_text(full)
        if not q_text:
            return None

        return {
            "level": level,
            "question_type": qtype,
            "question_text": _clean(q_text),
            "option_a": _clean(a),
            "option_b": _clean(b),
            "option_c": _clean(c),
            "option_d": _clean(d),
            "passage": _clean(passage),
            "source_url": source_url,
        }

    def _extract_options(self, text: str) -> tuple[str, str, str, str] | None:
        """Try to extract 4 options from text on one or few lines (inline format)."""
        m = _RE_OPTION_INLINE.search(text)
        if m:
            return m.group(1), m.group(2), m.group(3), m.group(4)
        return None

    def _extract_options_multiline(self, lines: list[str]) -> tuple[str, str, str, str] | None:
        """Extract options when they appear on separate lines."""
        opts: list[str] = []
        for line in lines:
            m = re.match(r"^\s*[1-4１-４][　\s\.\)]+(.+)", line.strip(), re.UNICODE)
            if m:
                opts.append(m.group(1).strip())
        if len(opts) >= 4:
            return opts[0], opts[1], opts[2], opts[3]
        return None

    def _extract_question_text(self, text: str) -> str:
        """Return the question text (strip leading question number + trailing options)."""
        # Remove leading number
        text = re.sub(r"^\s*\d{1,2}[．\.\s　]+", "", text, count=1, flags=re.UNICODE)
        # Cut off at first option marker (1 followed by non-digit and non-space ... or similar)
        cut = re.search(r"\s+[1１][　\s]", text)
        if cut:
            text = text[: cut.start()]
        return text.strip()
