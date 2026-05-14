import time
import logging
from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class BaseCrawler(ABC):
    """
    Abstract base crawler for JLPT quiz sites.

    Subclasses must implement the ``crawl`` method.

    Each question dict returned by ``crawl`` uses the following keys:

    ============== =====================================================
    Key            Description
    ============== =====================================================
    level          JLPT level string, e.g. ``"N3"``
    question_type  ``"vocabulary"`` | ``"grammar"`` | ``"reading"``
    question_text  The question stem (Japanese text)
    option_a       Choice A text
    option_b       Choice B text
    option_c       Choice C text
    option_d       Choice D text
    correct_answer ``"A"`` | ``"B"`` | ``"C"`` | ``"D"``
    explanation    Answer explanation (Japanese or bilingual)
    source_url     Canonical URL the question was parsed from
    passage        *(optional)* Reading passage associated with the
                   question; empty string when not applicable
    ============== =====================================================
    """

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;"
            "q=0.9,image/avif,image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8,vi;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    def __init__(self, base_url: str, delay: float = 2.0) -> None:
        """
        Initialise the crawler.

        Args:
            base_url: Root URL of the target site (trailing slash is stripped).
            delay:    Seconds to sleep before every HTTP request.
        """
        self.base_url = base_url.rstrip("/")
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def fetch(self, url: str) -> BeautifulSoup | None:
        """
        Fetch *url* and return a :class:`bs4.BeautifulSoup` document.

        Sleeps for ``self.delay`` seconds before making the request so we
        remain polite to the remote server.  Returns ``None`` on any
        network or HTTP error, logging the exception details.
        """
        time.sleep(self.delay)
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.HTTPError as exc:
            logger.error("HTTP error fetching %s: %s", url, exc)
        except requests.exceptions.ConnectionError as exc:
            logger.error("Connection error fetching %s: %s", url, exc)
        except requests.exceptions.Timeout:
            logger.error("Timeout fetching %s", url)
        except requests.exceptions.RequestException as exc:
            logger.error("Unexpected request error fetching %s: %s", url, exc)
        return None

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abstractmethod
    def crawl(self, level: str, question_type: str, max_pages: int = 5) -> list[dict]:
        """
        Crawl the target site and return a list of question dicts.

        Args:
            level:         JLPT level string, e.g. ``"N3"``.
            question_type: One of ``"vocabulary"``, ``"grammar"``,
                           ``"reading"``.
            max_pages:     Maximum number of paginated pages to visit.

        Returns:
            A (possibly empty) list of question dicts conforming to the
            schema described in the class docstring.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    @staticmethod
    def _empty_question(level: str, question_type: str, source_url: str) -> dict:
        """Return a blank question skeleton with all required keys."""
        return {
            "level": level,
            "question_type": question_type,
            "question_text": "",
            "option_a": "",
            "option_b": "",
            "option_c": "",
            "option_d": "",
            "correct_answer": "",
            "explanation": "",
            "source_url": source_url,
            "passage": "",
        }
