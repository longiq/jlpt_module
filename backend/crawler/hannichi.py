"""
Crawler for han-nichi.vercel.app via Supabase Storage.

Architecture discovered:
  - Frontend: han-nichi.vercel.app (Next.js on Vercel)
  - Backend:  uvyccqmvcxrctjqxnhgd.supabase.co (Supabase)
  - Data:     JSON files in Supabase Storage bucket "jlpt"
  - Naming:   {LEVEL}-{YEAR}-{MONTH}-{SESSION}.json
              e.g. N2-2025-7-1.json

Authentication:
  Priority 1 — Supabase email/password login
  Priority 2 — Bearer token passed directly (from browser DevTools)

Usage (standalone):
  python scripts/run_hannichi_crawl.py --level N2 --dry-run
  python scripts/run_hannichi_crawl.py --level all --token "eyJhbGci..." --save-to-db
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any, Optional

import requests

from .base import BaseCrawler

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SUPABASE_URL = "https://uvyccqmvcxrctjqxnhgd.supabase.co"
STORAGE_BUCKET = "jlpt"

JLPT_LEVELS = ["N1", "N2", "N3", "N4", "N5"]
# JLPT exams are held in July (7) and December (12).
EXAM_MONTHS = [7, 12]
# Cover recent years; extend as needed.
EXAM_YEARS = [2023, 2024, 2025, 2026]
# Multiple sessions per exam day (usually 1–2).
EXAM_SESSIONS = [1, 2]

# Field-name alternatives for flexible JSON mapping.
QUESTION_TEXT_KEYS = [
    "question_text", "question", "text", "content", "stem",
    "câu_hỏi", "question_jp", "mondai",
]
OPTIONS_KEYS = ["options", "choices", "answers", "selections", "sentakushi"]
CORRECT_KEYS = [
    "correct_answer", "correctAnswer", "answer", "correct",
    "key", "solution", "seikai",
]
EXPLANATION_KEYS = [
    "explanation", "explain", "giải_thích", "note", "hint",
    "reason", "kaisetsu",
]
PASSAGE_KEYS = [
    "passage", "reading", "context", "text", "content",
    "đoạn_văn", "mondaibun",
]

ANSWER_LABELS = ("A", "B", "C", "D")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def _pick(obj: dict, keys: list[str], default: Any = None) -> Any:
    for k in keys:
        if k in obj:
            return obj[k]
    return default


def _index_to_label(index: Any) -> str:
    try:
        i = int(index)
        return ANSWER_LABELS[i] if 0 <= i < 4 else ""
    except (TypeError, ValueError):
        return ""


# ---------------------------------------------------------------------------
# Main crawler class
# ---------------------------------------------------------------------------

class HanNichiCrawler(BaseCrawler):
    """
    Crawler for han-nichi.vercel.app via Supabase Storage JSON files.

    Data is stored as signed-URL-accessible JSON objects in the "jlpt" bucket
    under the naming scheme::

        {LEVEL}-{YEAR}-{MONTH}-{SESSION}.json
        e.g. N2-2025-7-1.json
    """

    def __init__(
        self,
        username: str = "duyhai",
        password: str = "Abc12345",
        token: Optional[str] = None,
        delay: float = 1.0,
    ) -> None:
        """
        Args:
            username: Supabase auth email or username.
            password: Supabase auth password.
            token:    Pre-obtained Bearer token (skips login step when provided).
            delay:    Seconds to sleep between HTTP requests.
        """
        super().__init__(base_url=SUPABASE_URL, delay=delay)
        self.username = username
        self.password = password
        self._token: Optional[str] = token
        self._authenticated: bool = token is not None
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
        })
        if token:
            self._apply_token(token)

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def _apply_token(self, token: str) -> None:
        self._token = token
        self.session.headers["Authorization"] = f"Bearer {token}"

    def authenticate(self) -> bool:
        """Login via Supabase Auth.  Returns True on success."""
        if self._authenticated:
            return True

        logger.info("[hannichi] authenticating as '%s'", self.username)

        # Try email-as-is, then common email suffixes.
        email_candidates = [self.username]
        if "@" not in self.username:
            email_candidates += [
                f"{self.username}@gmail.com",
                f"{self.username}@hannichi.com",
                f"{self.username}@han-nichi.com",
            ]

        for email in email_candidates:
            if self._try_supabase_login(email):
                self._authenticated = True
                logger.info("[hannichi] authenticated with email: %s", email)
                return True

        logger.error("[hannichi] all login attempts failed")
        return False

    def _try_supabase_login(self, email: str) -> bool:
        time.sleep(self.delay)
        try:
            resp = self.session.post(
                f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
                json={"email": email, "password": self.password},
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                token = data.get("access_token") or data.get("token")
                if token:
                    self._apply_token(token)
                    return True
            logger.debug(
                "[hannichi] login %s → %s: %s",
                email, resp.status_code, resp.text[:120],
            )
        except Exception as exc:
            logger.debug("[hannichi] login error for %s: %s", email, exc)
        return False

    # ------------------------------------------------------------------
    # Storage helpers
    # ------------------------------------------------------------------

    def _list_bucket(self) -> list[str]:
        """
        List all objects in the 'jlpt' storage bucket.
        Returns a list of file paths (e.g. ['N2-2025-7-1.json', ...]).
        """
        time.sleep(self.delay)
        try:
            resp = self.session.post(
                f"{SUPABASE_URL}/storage/v1/object/list/{STORAGE_BUCKET}",
                json={"limit": 1000, "offset": 0, "prefix": ""},
                timeout=15,
            )
            if resp.status_code == 200:
                items = resp.json()
                paths = [item["name"] for item in items if item.get("name")]
                logger.info("[hannichi] bucket listing: %d files found", len(paths))
                return paths
            logger.warning(
                "[hannichi] bucket list failed: %s %s",
                resp.status_code, resp.text[:200],
            )
        except Exception as exc:
            logger.warning("[hannichi] bucket list error: %s", exc)
        return []

    def _get_signed_url(self, file_path: str) -> Optional[str]:
        """Generate a fresh 5-minute signed URL for *file_path*."""
        time.sleep(self.delay)
        try:
            resp = self.session.post(
                f"{SUPABASE_URL}/storage/v1/object/sign/{STORAGE_BUCKET}/{file_path}",
                json={"expiresIn": 300},
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                signed = data.get("signedURL") or data.get("signedUrl")
                if signed:
                    # Make absolute if relative.
                    if signed.startswith("/"):
                        signed = SUPABASE_URL + signed
                    return signed
            logger.debug(
                "[hannichi] sign URL for %s → %s", file_path, resp.status_code
            )
        except Exception as exc:
            logger.debug("[hannichi] sign URL error %s: %s", file_path, exc)
        return None

    def _download_json(self, file_path: str) -> Optional[Any]:
        """Download and parse a JSON file from storage."""
        # Strategy 1: signed URL
        signed = self._get_signed_url(file_path)
        if signed:
            try:
                resp = requests.get(signed, timeout=15)
                if resp.status_code == 200:
                    return resp.json()
                logger.debug(
                    "[hannichi] signed download %s → %s", file_path, resp.status_code
                )
            except Exception as exc:
                logger.debug("[hannichi] signed download error: %s", exc)

        # Strategy 2: authenticated direct download
        time.sleep(self.delay)
        try:
            resp = self.session.get(
                f"{SUPABASE_URL}/storage/v1/object/{STORAGE_BUCKET}/{file_path}",
                timeout=15,
            )
            if resp.status_code == 200:
                return resp.json()
            logger.debug(
                "[hannichi] direct download %s → %s", file_path, resp.status_code
            )
        except Exception as exc:
            logger.debug("[hannichi] direct download error: %s", exc)
        return None

    def _candidate_files(self, level: str) -> list[str]:
        """
        Return the full list of candidate file paths for *level*.
        Tries real bucket listing first; falls back to enumeration.
        """
        bucket_files = self._list_bucket()
        if bucket_files:
            pattern = re.compile(
                rf"^{re.escape(level)}-\d+-\d+-\d+\.json$", re.IGNORECASE
            )
            matched = [f for f in bucket_files if pattern.match(f)]
            if matched:
                logger.info(
                    "[hannichi] found %d file(s) for %s in bucket", len(matched), level
                )
                return sorted(matched)

        # Enumerate known exam dates.
        candidates = []
        for year in EXAM_YEARS:
            for month in EXAM_MONTHS:
                for session in EXAM_SESSIONS:
                    candidates.append(f"{level}-{year}-{month}-{session}.json")
        logger.info(
            "[hannichi] using %d enumerated candidates for %s", len(candidates), level
        )
        return candidates

    # ------------------------------------------------------------------
    # Question mapping
    # ------------------------------------------------------------------

    def _map_questions_from_file(
        self,
        data: Any,
        level: str,
        question_type: str,
        source_url: str,
    ) -> list[dict]:
        """Convert raw JSON file contents to a list of Question dicts."""
        records: list[dict] = []

        if isinstance(data, list):
            raw_records = [r for r in data if isinstance(r, dict)]
        elif isinstance(data, dict):
            # Unwrap common envelope keys.
            raw_records = []
            for key in (
                "questions", "data", "items", "results",
                question_type, level,
            ):
                inner = data.get(key)
                if isinstance(inner, list):
                    raw_records = [r for r in inner if isinstance(r, dict)]
                    break
            if not raw_records:
                # Might be a single question object.
                if any(k in data for k in QUESTION_TEXT_KEYS):
                    raw_records = [data]
        else:
            return []

        for raw in raw_records:
            q = self._map_single(raw, level, question_type, source_url)
            if q:
                records.append(q)
        return records

    def _map_single(
        self,
        raw: dict,
        level: str,
        question_type: str,
        source_url: str,
    ) -> Optional[dict]:
        question_text = _clean(_pick(raw, QUESTION_TEXT_KEYS))
        if not question_text:
            return None

        # Options -------------------------------------------------------
        options_raw = _pick(raw, OPTIONS_KEYS)
        option_a = option_b = option_c = option_d = ""

        if isinstance(options_raw, list):
            texts = []
            for o in options_raw:
                if isinstance(o, dict):
                    texts.append(_clean(o.get("text") or o.get("value") or o.get("label") or ""))
                else:
                    texts.append(_clean(o))
            texts += [""] * (4 - len(texts))
            option_a, option_b, option_c, option_d = texts[:4]
        elif isinstance(options_raw, dict):
            option_a = _clean(options_raw.get("A") or options_raw.get("a") or "")
            option_b = _clean(options_raw.get("B") or options_raw.get("b") or "")
            option_c = _clean(options_raw.get("C") or options_raw.get("c") or "")
            option_d = _clean(options_raw.get("D") or options_raw.get("d") or "")
        else:
            option_a = _clean(raw.get("A") or raw.get("option_a") or raw.get("optionA") or "")
            option_b = _clean(raw.get("B") or raw.get("option_b") or raw.get("optionB") or "")
            option_c = _clean(raw.get("C") or raw.get("option_c") or raw.get("optionC") or "")
            option_d = _clean(raw.get("D") or raw.get("option_d") or raw.get("optionD") or "")

        if not option_a:
            return None

        # Correct answer ------------------------------------------------
        raw_correct = _pick(raw, CORRECT_KEYS, "")
        if isinstance(raw_correct, (int, float)):
            correct_answer = _index_to_label(int(raw_correct))
        elif isinstance(raw_correct, str):
            if raw_correct.upper() in ANSWER_LABELS:
                correct_answer = raw_correct.upper()
            elif raw_correct.isdigit():
                correct_answer = _index_to_label(raw_correct)
            else:
                # Try matching text against options.
                opts = [option_a, option_b, option_c, option_d]
                ct = _clean(raw_correct)
                correct_answer = (
                    ANSWER_LABELS[opts.index(ct)] if ct in opts else "A"
                )
        elif isinstance(raw_correct, dict):
            ct = _clean(raw_correct.get("text", ""))
            opts = [option_a, option_b, option_c, option_d]
            correct_answer = ANSWER_LABELS[opts.index(ct)] if ct in opts else "A"
        else:
            correct_answer = "A"

        # Explanation & passage -----------------------------------------
        explanation = _clean(_pick(raw, EXPLANATION_KEYS, ""))
        passage = ""
        if question_type == "reading":
            passage = _clean(_pick(raw, PASSAGE_KEYS, ""))

        # Level override ------------------------------------------------
        raw_level = _clean(_pick(raw, ["level", "jlpt", "jlpt_level"], ""))
        resolved_level = (
            raw_level.upper()
            if raw_level.upper() in ("N1", "N2", "N3", "N4", "N5")
            else level
        )

        # Question type override ----------------------------------------
        raw_type = _clean(_pick(raw, ["question_type", "type", "category", "mondai_type"], ""))
        type_map = {
            "vocab": "vocabulary", "vocabulary": "vocabulary", "tu_vung": "vocabulary",
            "grammar": "grammar", "ngu_phap": "grammar", "bunpo": "grammar",
            "reading": "reading", "doc_hieu": "reading", "dokkai": "reading",
            "listening": "listening", "nghe": "listening", "choukai": "listening",
        }
        resolved_type = type_map.get(raw_type.lower(), question_type)

        return {
            "level": resolved_level,
            "question_type": resolved_type,
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

    # ------------------------------------------------------------------
    # Core crawl logic
    # ------------------------------------------------------------------

    def crawl(
        self,
        level: str,
        question_type: str,
        max_pages: int = 10,
    ) -> list[dict]:
        """
        Download JSON exam files for *level* and return Question dicts.

        Args:
            level:         JLPT level string, e.g. ``"N2"``.
            question_type: ``"vocabulary"`` | ``"grammar"`` | ``"reading"``
                           | ``"listening"``.
            max_pages:     Maximum number of files to download (each exam
                           date = one file).

        Returns:
            List of question dicts conforming to the project schema.
        """
        logger.info(
            "[hannichi] crawl start — level=%s type=%s", level, question_type
        )

        if not self._authenticated and not self.authenticate():
            return []

        candidates = self._candidate_files(level)
        all_questions: list[dict] = []
        seen: set[str] = set()
        files_tried = 0

        for file_path in candidates:
            if files_tried >= max_pages:
                break

            logger.info("[hannichi] downloading %s", file_path)
            data = self._download_json(file_path)
            files_tried += 1

            if data is None:
                logger.debug("[hannichi] %s not found or error, skipping", file_path)
                continue

            source_url = f"{SUPABASE_URL}/storage/v1/object/{STORAGE_BUCKET}/{file_path}"
            questions = self._map_questions_from_file(
                data, level, question_type, source_url
            )

            new = 0
            for q in questions:
                key = q["question_text"]
                if key not in seen:
                    seen.add(key)
                    all_questions.append(q)
                    new += 1

            logger.info(
                "[hannichi] %s → %d questions (%d new, total=%d)",
                file_path, len(questions), new, len(all_questions),
            )

        logger.info(
            "[hannichi] crawl complete — %d questions from %d file(s)",
            len(all_questions), files_tried,
        )
        return all_questions

    def crawl_all_levels(
        self,
        question_type: str = "all",
        max_files_per_level: int = 10,
    ) -> list[dict]:
        """Convenience method: crawl all 5 JLPT levels at once."""
        all_q: list[dict] = []
        types = (
            ["vocabulary", "grammar", "reading", "listening"]
            if question_type == "all"
            else [question_type]
        )
        for level in JLPT_LEVELS:
            for qtype in types:
                all_q.extend(
                    self.crawl(level, qtype, max_pages=max_files_per_level)
                )
        return all_q
