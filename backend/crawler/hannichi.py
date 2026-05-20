"""
Crawler for han-nichi.vercel.app — an internal Japanese language learning app.

Authentication strategy (tried in order):
  1. NextAuth.js credentials flow: GET /api/auth/csrf → POST /api/auth/signin/credentials
  2. Simple JSON login: POST /api/login
  3. Simple JSON login: POST /api/auth/login

After a successful login the session cookies are retained automatically by
``requests.Session``.  Data is fetched via JSON API endpoints and mapped to
the Question schema used by this project.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Optional

import requests

from .base import BaseCrawler

logger = logging.getLogger(__name__)

SITE_BASE = "https://han-nichi.vercel.app"

# Ordered list of API endpoints to probe for question data.
# Each entry is a URL template; {level} and {type} are substituted at runtime.
CANDIDATE_ENDPOINTS: list[str] = [
    "/api/questions?level={level}&type={type}",
    "/api/questions?level={level}&question_type={type}",
    "/api/questions/{level}/{type}",
    "/api/quiz?level={level}&type={type}",
    "/api/vocabulary?level={level}",
    "/api/grammar?level={level}",
    "/api/reading?level={level}",
    "/api/words?level={level}",
    "/api/questions?level={level}",
    "/api/questions",
]

# Field name alternatives for question text.
QUESTION_TEXT_KEYS = ["question_text", "question", "text", "content", "stem", "câu_hỏi", "title"]
# Field name alternatives for answer choices.
OPTIONS_KEYS = ["options", "choices", "answers", "selections"]
# Field name alternatives for the correct answer.
CORRECT_KEYS = ["correct_answer", "correctAnswer", "answer", "correct", "key", "solution"]
# Field name alternatives for explanation.
EXPLANATION_KEYS = ["explanation", "explain", "giải_thích", "note", "hint", "reason"]
# Field name alternatives for a reading passage.
PASSAGE_KEYS = ["passage", "reading", "context", "text", "content", "đoạn_văn"]

ANSWER_LABELS = ("A", "B", "C", "D")


def _clean(value: Any) -> str:
    """Coerce *value* to a stripped string."""
    if value is None:
        return ""
    return " ".join(str(value).split())


def _pick(obj: dict, keys: list[str], default: Any = None) -> Any:
    """Return the first value found in *obj* for any key in *keys*."""
    for k in keys:
        if k in obj:
            return obj[k]
    return default


def _index_to_label(index: Any) -> str:
    """Convert a 0-based integer index (or string '0'-'3') to 'A'-'D'."""
    try:
        i = int(index)
        return ANSWER_LABELS[i] if 0 <= i < 4 else ""
    except (TypeError, ValueError):
        return ""


class HanNichiCrawler(BaseCrawler):
    """Crawler targeting https://han-nichi.vercel.app (requires authentication)."""

    def __init__(
        self,
        username: str = "duyhai",
        password: str = "Abc12345",
        delay: float = 1.5,
    ) -> None:
        super().__init__(base_url=SITE_BASE, delay=delay)
        self.username = username
        self.password = password
        self._authenticated = False
        # Accept JSON in addition to HTML.
        self.session.headers.update({
            "Accept": "application/json, text/html, */*",
            "Content-Type": "application/json",
        })

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def authenticate(self) -> bool:
        """Attempt login via all known strategies.  Returns True on success."""
        if self._authenticated:
            return True

        logger.info("[hannichi] attempting authentication as '%s'", self.username)

        if self._try_nextauth():
            self._authenticated = True
            logger.info("[hannichi] authenticated via NextAuth.js")
            return True

        if self._try_simple_login("/api/login"):
            self._authenticated = True
            logger.info("[hannichi] authenticated via /api/login")
            return True

        if self._try_simple_login("/api/auth/login"):
            self._authenticated = True
            logger.info("[hannichi] authenticated via /api/auth/login")
            return True

        logger.error("[hannichi] all authentication strategies failed")
        return False

    def _try_nextauth(self) -> bool:
        """NextAuth.js credentials provider flow."""
        try:
            time.sleep(self.delay)
            csrf_resp = self.session.get(
                f"{self.base_url}/api/auth/csrf", timeout=15
            )
            if csrf_resp.status_code != 200:
                logger.debug("[hannichi] /api/auth/csrf → %s", csrf_resp.status_code)
                return False

            csrf_token = csrf_resp.json().get("csrfToken", "")
            if not csrf_token:
                logger.debug("[hannichi] csrfToken not found in response")
                return False

            time.sleep(self.delay)
            signin_resp = self.session.post(
                f"{self.base_url}/api/auth/signin/credentials",
                json={
                    "username": self.username,
                    "password": self.password,
                    "csrfToken": csrf_token,
                    "redirect": "false",
                    "callbackUrl": self.base_url,
                },
                timeout=15,
                allow_redirects=True,
            )

            if signin_resp.status_code in (200, 302):
                # Verify we actually got a session by calling /api/auth/session
                time.sleep(self.delay)
                session_resp = self.session.get(
                    f"{self.base_url}/api/auth/session", timeout=15
                )
                if session_resp.status_code == 200:
                    data = session_resp.json()
                    if data.get("user") or data.get("token"):
                        return True

            logger.debug(
                "[hannichi] NextAuth flow returned %s", signin_resp.status_code
            )
        except Exception as exc:
            logger.debug("[hannichi] NextAuth flow error: %s", exc)
        return False

    def _try_simple_login(self, path: str) -> bool:
        """Try a simple JSON POST to *path* with username/password."""
        try:
            time.sleep(self.delay)
            resp = self.session.post(
                f"{self.base_url}{path}",
                json={"username": self.username, "password": self.password},
                timeout=15,
                allow_redirects=True,
            )
            if resp.status_code in (200, 201):
                body = {}
                try:
                    body = resp.json()
                except Exception:
                    pass
                # Accept if response contains a token or user data, or is just 200 OK.
                if (
                    body.get("token")
                    or body.get("accessToken")
                    or body.get("access_token")
                    or body.get("user")
                    or body.get("success")
                    or resp.status_code == 200
                ):
                    token = (
                        body.get("token")
                        or body.get("accessToken")
                        or body.get("access_token")
                    )
                    if token:
                        self.session.headers.update(
                            {"Authorization": f"Bearer {token}"}
                        )
                    return True
            logger.debug("[hannichi] %s → %s", path, resp.status_code)
        except Exception as exc:
            logger.debug("[hannichi] %s error: %s", path, exc)
        return False

    # ------------------------------------------------------------------
    # JSON fetch helper
    # ------------------------------------------------------------------

    def fetch_json(self, url: str) -> Optional[Any]:
        """GET *url* and return parsed JSON, or None on error."""
        time.sleep(self.delay)
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as exc:
            logger.debug("[hannichi] HTTP error %s: %s", url, exc)
        except requests.exceptions.ConnectionError as exc:
            logger.debug("[hannichi] Connection error %s: %s", url, exc)
        except requests.exceptions.Timeout:
            logger.debug("[hannichi] Timeout %s", url)
        except Exception as exc:
            logger.debug("[hannichi] fetch_json error %s: %s", url, exc)
        return None

    # ------------------------------------------------------------------
    # Endpoint discovery
    # ------------------------------------------------------------------

    def _discover_endpoint(self, level: str, question_type: str) -> Optional[str]:
        """
        Try candidate endpoints and return the first that returns usable data.
        Returns the full URL string, or None if nothing worked.
        """
        for template in CANDIDATE_ENDPOINTS:
            url = self.base_url + template.format(level=level, type=question_type)
            logger.debug("[hannichi] probing %s", url)
            data = self.fetch_json(url)
            if data is None:
                continue
            records = self._extract_records(data)
            if records:
                logger.info(
                    "[hannichi] found %d record(s) at %s", len(records), url
                )
                return url
            logger.debug("[hannichi] %s returned data but no records", url)

        logger.warning(
            "[hannichi] no working endpoint found for level=%s type=%s",
            level,
            question_type,
        )
        return None

    def _extract_records(self, data: Any) -> list[dict]:
        """Normalise API response to a flat list of record dicts."""
        if isinstance(data, list):
            return [r for r in data if isinstance(r, dict)]
        if isinstance(data, dict):
            # Unwrap common envelope patterns.
            for key in ("data", "questions", "items", "results", "records", "content"):
                inner = data.get(key)
                if isinstance(inner, list):
                    return [r for r in inner if isinstance(r, dict)]
            # Response itself might be a single question record.
            if any(k in data for k in QUESTION_TEXT_KEYS):
                return [data]
        return []

    # ------------------------------------------------------------------
    # Question mapping
    # ------------------------------------------------------------------

    def _map_to_question(
        self,
        raw: dict,
        level: str,
        question_type: str,
        source_url: str,
    ) -> Optional[dict]:
        """Map a raw API record to a Question dict.  Returns None if unusable."""
        question_text = _clean(_pick(raw, QUESTION_TEXT_KEYS))
        if not question_text:
            return None

        # --- options -------------------------------------------------------
        options_raw = _pick(raw, OPTIONS_KEYS)
        option_a = option_b = option_c = option_d = ""

        if isinstance(options_raw, list):
            texts = [_clean(o.get("text", o) if isinstance(o, dict) else o)
                     for o in options_raw]
            texts += [""] * (4 - len(texts))
            option_a, option_b, option_c, option_d = texts[:4]
        elif isinstance(options_raw, dict):
            option_a = _clean(options_raw.get("A") or options_raw.get("a") or "")
            option_b = _clean(options_raw.get("B") or options_raw.get("b") or "")
            option_c = _clean(options_raw.get("C") or options_raw.get("c") or "")
            option_d = _clean(options_raw.get("D") or options_raw.get("d") or "")
        else:
            # Try direct A/B/C/D keys on the record.
            option_a = _clean(raw.get("A") or raw.get("option_a") or raw.get("optionA") or "")
            option_b = _clean(raw.get("B") or raw.get("option_b") or raw.get("optionB") or "")
            option_c = _clean(raw.get("C") or raw.get("option_c") or raw.get("optionC") or "")
            option_d = _clean(raw.get("D") or raw.get("option_d") or raw.get("optionD") or "")

        if not option_a:
            return None  # Minimum: at least option A must exist.

        # --- correct answer ------------------------------------------------
        raw_correct = _pick(raw, CORRECT_KEYS, "")
        if isinstance(raw_correct, int) or (
            isinstance(raw_correct, str) and raw_correct.isdigit()
        ):
            correct_answer = _index_to_label(raw_correct)
        elif isinstance(raw_correct, str) and raw_correct.upper() in ANSWER_LABELS:
            correct_answer = raw_correct.upper()
        else:
            # If correct is an option dict with a 'text' key, match against options.
            correct_text = _clean(
                raw_correct.get("text", "") if isinstance(raw_correct, dict) else raw_correct
            )
            opts = [option_a, option_b, option_c, option_d]
            if correct_text and correct_text in opts:
                correct_answer = ANSWER_LABELS[opts.index(correct_text)]
            else:
                correct_answer = "A"  # Default fallback.

        # --- explanation ---------------------------------------------------
        explanation = _clean(_pick(raw, EXPLANATION_KEYS, ""))

        # --- passage (reading questions) -----------------------------------
        passage = ""
        if question_type == "reading":
            passage = _clean(_pick(raw, PASSAGE_KEYS, ""))

        # --- level override ------------------------------------------------
        raw_level = _clean(_pick(raw, ["level", "jlpt", "jlpt_level"], ""))
        resolved_level = raw_level.upper() if raw_level.upper() in ("N1","N2","N3","N4","N5") else level

        return {
            "level": resolved_level,
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

    # ------------------------------------------------------------------
    # Core crawl logic
    # ------------------------------------------------------------------

    def crawl(self, level: str, question_type: str, max_pages: int = 5) -> list[dict]:
        """
        Authenticate, discover the data endpoint, and return question dicts.

        Args:
            level:         JLPT level, e.g. ``"N3"``.
            question_type: ``"vocabulary"`` | ``"grammar"`` | ``"reading"``.
            max_pages:     Maximum paginated pages to fetch.

        Returns:
            List of question dicts; empty if auth or endpoint discovery fails.
        """
        logger.info(
            "[hannichi] crawl start — level=%s type=%s max_pages=%s",
            level, question_type, max_pages,
        )

        if not self.authenticate():
            return []

        endpoint_url = self._discover_endpoint(level, question_type)
        if endpoint_url is None:
            return []

        all_questions: list[dict] = []
        seen: set[str] = set()

        for page in range(1, max_pages + 1):
            # Build paginated URL.
            sep = "&" if "?" in endpoint_url else "?"
            if max_pages > 1:
                paged_url = f"{endpoint_url}{sep}page={page}&limit=50"
            else:
                paged_url = endpoint_url

            logger.info("[hannichi] fetching page %d: %s", page, paged_url)
            data = self.fetch_json(paged_url)
            if data is None:
                logger.warning("[hannichi] page %d fetch failed; stopping", page)
                break

            records = self._extract_records(data)
            if not records:
                logger.info("[hannichi] no records on page %d; stopping", page)
                break

            new_count = 0
            for raw in records:
                q = self._map_to_question(raw, level, question_type, paged_url)
                if q is None:
                    continue
                key = q["question_text"]
                if key in seen:
                    continue
                seen.add(key)
                all_questions.append(q)
                new_count += 1

            logger.info(
                "[hannichi] page %d: %d new questions (total: %d)",
                page, new_count, len(all_questions),
            )

            if new_count == 0:
                logger.info("[hannichi] no new questions; stopping pagination")
                break

            # Stop if we got fewer records than requested (last page).
            if len(records) < 50:
                break

        logger.info(
            "[hannichi] crawl complete — %d questions returned", len(all_questions)
        )
        return all_questions
