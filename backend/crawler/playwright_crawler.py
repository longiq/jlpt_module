"""
Automate han-nichi.vercel.app with Playwright: login, enumerate exams, download PDFs.

Architecture:
  - Login with Supabase credentials (duyhai / Abc12345)
  - Navigate to exam list page, enumerate all exams per level
  - For each exam: trigger PDF export and save to output_dir
  - Returns list[dict] with: pdf_path, level, exam_id, source_url

NOTE: han-nichi.vercel.app blocks datacenter IPs via Cloudflare WAF.
      Run this from a residential/office IP or set HTTP_PROXY / HTTPS_PROXY.
      Set PLAYWRIGHT_PROXY env var to use a SOCKS5/HTTP proxy, e.g.:
          export PLAYWRIGHT_PROXY="socks5://user:pass@host:port"
"""

from __future__ import annotations

import logging
import os
import re
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

BASE_URL = "https://han-nichi.vercel.app"
USERNAME = "duyhai"
PASSWORD = "Abc12345"
JLPT_LEVELS = ["N1", "N2", "N3", "N4", "N5"]


def _proxy_settings() -> Optional[dict]:
    proxy = os.environ.get("PLAYWRIGHT_PROXY") or os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY")
    if proxy:
        return {"server": proxy}
    return None


class PlaywrightCrawler:
    """Download JLPT exam PDFs from han-nichi.vercel.app using Playwright."""

    def __init__(
        self,
        username: str = USERNAME,
        password: str = PASSWORD,
        headless: bool = True,
        slow_mo: int = 300,
    ) -> None:
        self.username = username
        self.password = password
        self.headless = headless
        self.slow_mo = slow_mo

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def download_all_pdfs(
        self,
        output_dir: str,
        level: Optional[str] = None,
    ) -> list[dict]:
        """
        Login, enumerate exams, and download each as PDF.

        Args:
            output_dir: Directory to save downloaded PDFs.
            level:      If set, only download exams for this level (e.g. "N2").
                        If None, downloads all levels.

        Returns:
            list of dicts: [{pdf_path, level, exam_id, source_url}, ...]
        """
        try:
            from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
        except ImportError:
            raise ImportError(
                "playwright is required: pip install playwright && python -m playwright install chromium"
            )

        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        levels = [level.upper()] if level else JLPT_LEVELS
        results: list[dict] = []

        proxy = _proxy_settings()
        if proxy:
            logger.info("[pw_crawler] using proxy: %s", proxy["server"])

        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo,
                proxy=proxy,
            )
            context = browser.new_context(
                viewport={"width": 1280, "height": 900},
                locale="ja-JP",
                accept_downloads=True,
            )
            page = context.new_page()

            try:
                if not self._login(page):
                    logger.error("[pw_crawler] login failed, aborting")
                    return []

                for lv in levels:
                    exams = self._list_exams(page, lv)
                    logger.info("[pw_crawler] %s: %d exam(s) found", lv, len(exams))
                    for exam in exams:
                        pdf_info = self._download_exam_pdf(page, exam, out_path)
                        if pdf_info:
                            results.append(pdf_info)
                        time.sleep(1.0)
            finally:
                context.close()
                browser.close()

        logger.info("[pw_crawler] done — %d PDFs downloaded", len(results))
        return results

    # ------------------------------------------------------------------
    # Login
    # ------------------------------------------------------------------

    def _login(self, page: Any) -> bool:
        from playwright.sync_api import TimeoutError as PWTimeout

        logger.info("[pw_crawler] navigating to %s", BASE_URL)
        try:
            page.goto(BASE_URL, wait_until="networkidle", timeout=30_000)
        except Exception as exc:
            logger.error("[pw_crawler] goto failed: %s", exc)
            return False

        # Look for a login form or button
        try:
            # Try clicking a login/sign-in link if present
            login_link = page.locator("a[href*='login'], a[href*='sign'], button:has-text('ログイン'), button:has-text('Login'), button:has-text('Đăng nhập')")
            if login_link.count() > 0:
                login_link.first.click()
                page.wait_for_load_state("networkidle", timeout=10_000)
        except Exception:
            pass

        # Fill credentials — try common field selectors
        try:
            page.wait_for_selector("input[type='email'], input[name='email'], input[placeholder*='email' i]", timeout=10_000)
            email_field = page.locator("input[type='email'], input[name='email'], input[placeholder*='email' i]").first
            email_field.fill(self.username if "@" in self.username else f"{self.username}@gmail.com")

            pw_field = page.locator("input[type='password']").first
            pw_field.fill(self.password)

            submit = page.locator("button[type='submit'], button:has-text('ログイン'), button:has-text('Login'), button:has-text('Đăng nhập')").first
            submit.click()
            page.wait_for_load_state("networkidle", timeout=15_000)
            logger.info("[pw_crawler] login submitted, URL=%s", page.url)
            return True
        except PWTimeout:
            logger.error("[pw_crawler] login form not found or timed out")
            return False
        except Exception as exc:
            logger.error("[pw_crawler] login error: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Exam enumeration
    # ------------------------------------------------------------------

    def _list_exams(self, page: Any, level: str) -> list[dict]:
        """Navigate to the exam list for *level* and return exam metadata."""
        from playwright.sync_api import TimeoutError as PWTimeout

        # Try navigating to a level-specific page or filtering
        exam_url_candidates = [
            f"{BASE_URL}/de-thi?level={level}",
            f"{BASE_URL}/exams?level={level}",
            f"{BASE_URL}/{level.lower()}",
            f"{BASE_URL}/de-thi",
            f"{BASE_URL}/exams",
        ]

        for url in exam_url_candidates:
            try:
                page.goto(url, wait_until="networkidle", timeout=20_000)
                if page.url == url or level.lower() in page.url.lower() or "exam" in page.url.lower() or "de-thi" in page.url.lower():
                    break
            except Exception:
                continue

        # Try to find and click a level filter
        try:
            level_btn = page.locator(f"button:has-text('{level}'), a:has-text('{level}'), [data-level='{level}']")
            if level_btn.count() > 0:
                level_btn.first.click()
                page.wait_for_load_state("networkidle", timeout=10_000)
        except Exception:
            pass

        # Scrape exam cards/rows
        exams: list[dict] = []
        try:
            # Common patterns for exam list items
            cards = page.locator("a[href*='de-thi'], a[href*='exam'], [class*='exam'], [class*='card']")
            count = min(cards.count(), 50)  # cap to avoid infinite loop on wrong page
            for i in range(count):
                card = cards.nth(i)
                href = card.get_attribute("href") or ""
                text = card.inner_text().strip()

                # Detect level from card text or href
                detected_level = level
                for lv in JLPT_LEVELS:
                    if lv in text or lv.lower() in href.lower():
                        detected_level = lv
                        break

                if detected_level != level:
                    continue

                # Try to extract exam_id from href or text
                exam_id = self._extract_exam_id(href, text) or f"{level}-{i}"
                exam_url = href if href.startswith("http") else (BASE_URL + href if href.startswith("/") else BASE_URL)

                exams.append({
                    "level": detected_level,
                    "exam_id": exam_id,
                    "url": exam_url,
                    "href": href,
                })
        except Exception as exc:
            logger.warning("[pw_crawler] exam enumeration error: %s", exc)

        # Deduplicate by href
        seen: set[str] = set()
        unique: list[dict] = []
        for e in exams:
            key = e["href"]
            if key and key not in seen:
                seen.add(key)
                unique.append(e)

        return unique

    def _extract_exam_id(self, href: str, text: str) -> Optional[str]:
        # Try to match patterns like N2-2024-7, 2024-1, etc.
        for src in (href, text):
            m = re.search(r"(N[1-5])[_-](\d{4})[_-](\d+)", src, re.I)
            if m:
                return f"{m.group(1).upper()}-{m.group(2)}-{m.group(3)}"
            m = re.search(r"(\d{4})[_-](\d+)", src)
            if m:
                return f"{m.group(1)}-{m.group(2)}"
        return None

    # ------------------------------------------------------------------
    # PDF download
    # ------------------------------------------------------------------

    def _download_exam_pdf(self, page: Any, exam: dict, out_path: Path) -> Optional[dict]:
        """Navigate to exam page and download/generate PDF."""
        from playwright.sync_api import TimeoutError as PWTimeout

        level = exam["level"]
        exam_id = exam["exam_id"]
        exam_url = exam["url"]
        pdf_name = f"{level}-{exam_id}.pdf"
        pdf_path = out_path / pdf_name

        if pdf_path.exists():
            logger.info("[pw_crawler] skip (exists): %s", pdf_name)
            return {
                "pdf_path": str(pdf_path),
                "level": level,
                "exam_id": exam_id,
                "source_url": exam_url,
            }

        logger.info("[pw_crawler] downloading: %s", exam_url)
        try:
            page.goto(exam_url, wait_until="networkidle", timeout=20_000)
        except Exception as exc:
            logger.warning("[pw_crawler] goto %s failed: %s", exam_url, exc)
            return None

        # Strategy 1: Look for a download/PDF/print button
        pdf_saved = False
        try:
            dl_btn = page.locator(
                "button:has-text('PDF'), button:has-text('Print'), button:has-text('In'), "
                "button:has-text('Xuất'), a:has-text('PDF'), a[href*='.pdf'], "
                "[class*='print'], [class*='export'], [class*='download']"
            )
            if dl_btn.count() > 0:
                with page.expect_download(timeout=15_000) as dl_info:
                    dl_btn.first.click()
                dl = dl_info.value
                dl.save_as(str(pdf_path))
                pdf_saved = True
                logger.info("[pw_crawler] downloaded via button: %s", pdf_name)
        except PWTimeout:
            pass
        except Exception as exc:
            logger.debug("[pw_crawler] download button strategy failed: %s", exc)

        # Strategy 2: page.pdf() — Playwright can render page to PDF directly
        if not pdf_saved:
            try:
                page.pdf(path=str(pdf_path), format="A4", print_background=True)
                pdf_saved = True
                logger.info("[pw_crawler] rendered to PDF: %s", pdf_name)
            except Exception as exc:
                logger.warning("[pw_crawler] page.pdf() failed: %s", exc)

        if pdf_saved and pdf_path.exists() and pdf_path.stat().st_size > 1024:
            return {
                "pdf_path": str(pdf_path),
                "level": level,
                "exam_id": exam_id,
                "source_url": exam_url,
            }

        logger.warning("[pw_crawler] failed to obtain PDF for %s", exam_id)
        return None
