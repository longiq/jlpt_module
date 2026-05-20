"""
Crawler for han-nichi.vercel.app via Supabase Storage.

Discovered architecture:
  Frontend : han-nichi.vercel.app  (Next.js / Vercel)
  Backend  : uvyccqmvcxrctjqxnhgd.supabase.co  (Supabase)
  Storage  : bucket "jlpt", files named {LEVEL}-{YEAR}-{MONTH}-{SESSION}.json
             e.g. N2-2025-7-1.json

JSON file schema::

    {
      "level"   : "N2",
      "exam_id" : "2025-1",
      "sections": [
        {
          "sec": "問題2　___の言葉を漢字で書くとき...",
          "questions": [
            {
              "qid"    : 6,
              "ques"   : "6．このタオルはまだ<u>しめって</u>いる｡",
              "options": {"1": "1　渡って", "2": "2　温って",
                          "3": "3　汗って", "4": "4　湿って"},
              "answer" : "4",
              "expl"   : "湿る ẩm ướt；...",
              "pid"    : null          // non-null → reading question
            }
          ]
        }
      ],
      "passages": [
        {"pid": 0, "passage": "<div>...</div>"}
      ]
    }

Section → question_type mapping (per level):
    N1 : 問題1-4=vocabulary  問題5-7=grammar  問題8+=reading
    N2 : 問題1-6=vocabulary  問題7-8=grammar  問題9+=reading
    N3 : 問題1-8=vocabulary  問題9-10=grammar 問題11+=reading
    N4 : 問題1-4=vocabulary  問題5-8=grammar  問題9+=reading
    N5 : 問題1-4=vocabulary  問題5-7=grammar  問題8+=reading

Authentication flow:
  1. Supabase email/password  →  access_token  →  signed storage URLs
  2. Pre-supplied Bearer token (--token flag)  →  signed storage URLs

NOTE: Both han-nichi.vercel.app and uvyccqmvcxrctjqxnhgd.supabase.co block
      datacenter IPs.  Run this crawler on a machine with a residential/office IP,
      or pass --token with a token copied from browser DevTools.
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
# Supabase constants
# ---------------------------------------------------------------------------

SUPABASE_URL = "https://uvyccqmvcxrctjqxnhgd.supabase.co"
STORAGE_BUCKET = "jlpt"

JLPT_LEVELS = ["N1", "N2", "N3", "N4", "N5"]
# JLPT exams are held in July (7) and December (12).
EXAM_MONTHS = [7, 12]
EXAM_YEARS = [2023, 2024, 2025, 2026]
EXAM_SESSIONS = [1, 2]

# ---------------------------------------------------------------------------
# Section-number → question_type mapping per JLPT level
# Each tuple: (max_section_inclusive, question_type)
# ---------------------------------------------------------------------------
SECTION_TYPE_MAP: dict[str, list[tuple[int, str]]] = {
    "N1": [(4, "vocabulary"), (7, "grammar"),  (99, "reading")],
    "N2": [(6, "vocabulary"), (8, "grammar"),  (99, "reading")],
    "N3": [(8, "vocabulary"), (10, "grammar"), (99, "reading")],
    "N4": [(4, "vocabulary"), (8, "grammar"),  (99, "reading")],
    "N5": [(4, "vocabulary"), (7, "grammar"),  (99, "reading")],
}

# "1"→"A", "2"→"B", "3"→"C", "4"→"D"
OPTION_TO_LABEL = {"1": "A", "2": "B", "3": "C", "4": "D"}


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------

def _strip_html(text: str) -> str:
    """Remove HTML tags and normalise whitespace."""
    clean = re.sub(r"<[^>]+>", " ", text or "")
    return " ".join(clean.split())


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def _extract_section_num(sec_title: str) -> int:
    """Return the integer N from '問題N　...' or 0 if not found."""
    m = re.search(r"問題\s*(\d+)", sec_title)
    return int(m.group(1)) if m else 0


def _section_type(level: str, section_num: int) -> str:
    """Map (level, section_number) → 'vocabulary' | 'grammar' | 'reading'."""
    for max_sec, qtype in SECTION_TYPE_MAP.get(level, SECTION_TYPE_MAP["N2"]):
        if section_num <= max_sec:
            return qtype
    return "reading"


# ---------------------------------------------------------------------------
# Main crawler class
# ---------------------------------------------------------------------------

class HanNichiCrawler(BaseCrawler):
    """Crawler for han-nichi.vercel.app via Supabase Storage JSON files."""

    def __init__(
        self,
        username: str = "duyhai",
        password: str = "Abc12345",
        token: Optional[str] = None,
        delay: float = 1.0,
    ) -> None:
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
        if self._authenticated:
            return True
        logger.info("[hannichi] authenticating as '%s'", self.username)
        candidates = [self.username]
        if "@" not in self.username:
            candidates += [
                f"{self.username}@gmail.com",
                f"{self.username}@han-nichi.com",
            ]
        for email in candidates:
            if self._try_login(email):
                self._authenticated = True
                logger.info("[hannichi] authenticated: %s", email)
                return True
        logger.error("[hannichi] all login attempts failed")
        return False

    def _try_login(self, email: str) -> bool:
        time.sleep(self.delay)
        try:
            r = self.session.post(
                f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
                json={"email": email, "password": self.password},
                timeout=15,
            )
            if r.status_code == 200:
                token = r.json().get("access_token") or r.json().get("token")
                if token:
                    self._apply_token(token)
                    return True
            logger.debug("[hannichi] login %s → %s: %s", email, r.status_code, r.text[:80])
        except Exception as exc:
            logger.debug("[hannichi] login error %s: %s", email, exc)
        return False

    # ------------------------------------------------------------------
    # Storage helpers
    # ------------------------------------------------------------------

    def _list_bucket(self) -> list[str]:
        """List all objects in the 'jlpt' bucket."""
        time.sleep(self.delay)
        try:
            r = self.session.post(
                f"{SUPABASE_URL}/storage/v1/object/list/{STORAGE_BUCKET}",
                json={"limit": 1000, "offset": 0, "prefix": ""},
                timeout=15,
            )
            if r.status_code == 200:
                names = [item["name"] for item in r.json() if item.get("name")]
                logger.info("[hannichi] bucket: %d files", len(names))
                return names
            logger.warning("[hannichi] bucket list %s: %s", r.status_code, r.text[:100])
        except Exception as exc:
            logger.warning("[hannichi] bucket list error: %s", exc)
        return []

    def _signed_url(self, file_path: str) -> Optional[str]:
        """Generate a 5-minute signed URL for *file_path*."""
        time.sleep(self.delay)
        try:
            r = self.session.post(
                f"{SUPABASE_URL}/storage/v1/object/sign/{STORAGE_BUCKET}/{file_path}",
                json={"expiresIn": 300},
                timeout=15,
            )
            if r.status_code == 200:
                signed = r.json().get("signedURL") or r.json().get("signedUrl") or ""
                return (SUPABASE_URL + signed) if signed.startswith("/") else signed or None
            logger.debug("[hannichi] sign %s → %s", file_path, r.status_code)
        except Exception as exc:
            logger.debug("[hannichi] sign error %s: %s", file_path, exc)
        return None

    def _download(self, file_path: str) -> Optional[Any]:
        """Download a JSON file from storage (signed URL first, then direct)."""
        # Strategy 1: signed URL (no auth header needed on the download request)
        url = self._signed_url(file_path)
        if url:
            try:
                r = requests.get(url, timeout=20)
                if r.status_code == 200:
                    return r.json()
                logger.debug("[hannichi] signed GET %s → %s", file_path, r.status_code)
            except Exception as exc:
                logger.debug("[hannichi] signed GET error: %s", exc)

        # Strategy 2: authenticated direct download
        time.sleep(self.delay)
        try:
            r = self.session.get(
                f"{SUPABASE_URL}/storage/v1/object/{STORAGE_BUCKET}/{file_path}",
                timeout=20,
            )
            if r.status_code == 200:
                return r.json()
            logger.debug("[hannichi] direct GET %s → %s", file_path, r.status_code)
        except Exception as exc:
            logger.debug("[hannichi] direct GET error: %s", exc)
        return None

    def _candidate_files(self, level: str) -> list[str]:
        """Return file paths to attempt for *level* (bucket listing or enumeration)."""
        bucket = self._list_bucket()
        if bucket:
            pat = re.compile(rf"^{re.escape(level)}-\d+-\d+-\d+\.json$", re.I)
            matched = sorted(f for f in bucket if pat.match(f))
            if matched:
                logger.info("[hannichi] %d file(s) for %s from bucket", len(matched), level)
                return matched

        # Fallback: enumerate known exam dates
        files = [
            f"{level}-{yr}-{mo}-{ses}.json"
            for yr in EXAM_YEARS
            for mo in EXAM_MONTHS
            for ses in EXAM_SESSIONS
        ]
        logger.info("[hannichi] enumerated %d candidate files for %s", len(files), level)
        return files

    # ------------------------------------------------------------------
    # JSON parsing — exact schema
    # ------------------------------------------------------------------

    def _parse_file(
        self,
        data: dict,
        source_url: str,
        filter_type: Optional[str] = None,
    ) -> list[dict]:
        """
        Parse a han-nichi exam JSON file into Question dicts.

        Args:
            data:        Parsed JSON object from Supabase Storage.
            source_url:  URL used to download the file (stored as source_url).
            filter_type: If set, only return questions of this type.
        """
        level = _clean(data.get("level", "")).upper()
        if level not in JLPT_LEVELS:
            logger.warning("[hannichi] unknown level '%s' in file, skipping", level)
            return []

        # Build passage lookup: pid (int) → plain text
        passages: dict[int, str] = {}
        for p in data.get("passages", []):
            pid = p.get("pid")
            if pid is not None:
                passages[int(pid)] = _strip_html(p.get("passage", ""))

        results: list[dict] = []

        for section in data.get("sections", []):
            sec_title = _clean(section.get("sec", ""))
            sec_num = _extract_section_num(sec_title)
            qtype = _section_type(level, sec_num)

            if filter_type and filter_type != "all" and qtype != filter_type:
                continue

            for raw_q in section.get("questions", []):
                q = self._map_question(raw_q, level, qtype, source_url, passages, sec_title)
                if q:
                    results.append(q)

        logger.info(
            "[hannichi] parsed %d questions from %s (filter=%s)",
            len(results), source_url.split("/")[-1], filter_type or "all",
        )
        return results

    def _map_question(
        self,
        raw: dict,
        level: str,
        qtype: str,
        source_url: str,
        passages: dict[int, str],
        sec_title: str,
    ) -> Optional[dict]:
        """Map one raw question dict → Question schema dict."""

        # Question text — strip HTML tags (e.g. <u>, <b>)
        question_text = _strip_html(raw.get("ques", ""))
        if not question_text:
            return None

        # Options: {"1": "1　渡って", "2": ..., "3": ..., "4": ...}
        opts = raw.get("options", {})
        option_a = _clean(opts.get("1", ""))
        option_b = _clean(opts.get("2", ""))
        option_c = _clean(opts.get("3", ""))
        option_d = _clean(opts.get("4", ""))

        if not option_a:
            return None

        # Answer: "1"→"A", "2"→"B", "3"→"C", "4"→"D"
        correct_answer = OPTION_TO_LABEL.get(str(raw.get("answer", "")), "A")

        # Explanation
        explanation = _clean(raw.get("expl", ""))

        # Passage for reading questions
        passage = ""
        pid = raw.get("pid")
        if pid is not None:
            passage = passages.get(int(pid), "")

        return {
            "level": level,
            "question_type": qtype,
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
    # Core crawl
    # ------------------------------------------------------------------

    def crawl(
        self,
        level: str,
        question_type: str,
        max_pages: int = 10,
    ) -> list[dict]:
        """
        Download exam JSON files for *level* and return Question dicts.

        Each storage file contains ALL question types for that exam.
        *question_type* is used as a post-download filter.

        Args:
            level:         JLPT level, e.g. ``"N2"``.
            question_type: ``"vocabulary"`` | ``"grammar"`` | ``"reading"``
                           | ``"all"`` — filter applied after parsing.
            max_pages:     Max files to attempt (one file = one exam date).
        """
        logger.info("[hannichi] crawl — level=%s type=%s", level, question_type)

        if not self._authenticated and not self.authenticate():
            return []

        candidates = self._candidate_files(level)
        all_questions: list[dict] = []
        seen: set[str] = set()
        files_hit = 0

        for file_path in candidates:
            if files_hit >= max_pages:
                break

            data = self._download(file_path)
            files_hit += 1

            if data is None:
                logger.debug("[hannichi] %s not found, skipping", file_path)
                continue

            source_url = (
                f"{SUPABASE_URL}/storage/v1/object/{STORAGE_BUCKET}/{file_path}"
            )
            questions = self._parse_file(data, source_url, filter_type=question_type)

            added = 0
            for q in questions:
                key = f"{q['level']}|{q['question_text']}"
                if key not in seen:
                    seen.add(key)
                    all_questions.append(q)
                    added += 1

            logger.info(
                "[hannichi] %s → %d new (total=%d)", file_path, added, len(all_questions)
            )

        logger.info(
            "[hannichi] done — %d questions from %d file(s) tried",
            len(all_questions), files_hit,
        )
        return all_questions
