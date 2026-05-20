"""
Fill correct answers and bilingual explanations using the Anthropic API.

Each question dict is expected to have:
    level, question_type, question_text, option_a, option_b, option_c, option_d

After processing, each dict gains two new keys:
    correct_answer  : "A" | "B" | "C" | "D"
    explanation     : short Japanese sentence + Vietnamese meaning
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
Bạn là chuyên gia JLPT N1-N5. Với mỗi câu hỏi tiếng Nhật được đánh số, hãy phân tích và trả về đúng đáp án cùng giải thích ngắn.

Quy tắc bắt buộc:
1. Trả về JSON array, mỗi phần tử tương ứng một câu hỏi theo đúng thứ tự.
2. Mỗi phần tử: {"answer": "A"|"B"|"C"|"D", "explanation": "..."}
3. Giải thích: 1-2 câu tiếng Nhật giải thích tại sao đáp án đúng, kèm nghĩa tiếng Việt.
4. Chỉ trả về JSON array, không thêm bất kỳ text nào khác.
5. Số phần tử trong array phải BẰNG ĐÚNG số câu hỏi đầu vào.\
"""


class AIAnswerer:
    MODEL = "claude-sonnet-4-6"
    BATCH_SIZE = 10

    def __init__(self, api_key: str | None = None) -> None:
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic is required: pip install anthropic")
        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=key)

    # ------------------------------------------------------------------

    def fill_answers(self, questions: list[dict]) -> list[dict]:
        """
        Add correct_answer and explanation to each question dict (in-place).
        Returns the same list with those fields populated.
        Questions that fail to get an answer are left with defaults ("A", "").
        """
        results: list[dict] = []
        for i in range(0, len(questions), self.BATCH_SIZE):
            batch = questions[i : i + self.BATCH_SIZE]
            filled = self._process_batch(batch)
            results.extend(filled)
        return results

    # ------------------------------------------------------------------

    def _process_batch(self, batch: list[dict]) -> list[dict]:
        user_msg = self._format_batch(batch)
        try:
            response = self.client.messages.create(
                model=self.MODEL,
                max_tokens=2048,
                system=[
                    {
                        "type": "text",
                        "text": _SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=[{"role": "user", "content": user_msg}],
            )
            raw = response.content[0].text.strip()
            answers = self._parse_response(raw, len(batch))
        except Exception as exc:
            logger.error("[ai_answerer] API error: %s", exc)
            answers = [{"answer": "A", "explanation": ""} for _ in batch]

        for q, ans in zip(batch, answers):
            q["correct_answer"] = ans.get("answer", "A")
            q["explanation"] = ans.get("explanation", "")

        logger.info("[ai_answerer] batch %d → done", len(batch))
        return batch

    # ------------------------------------------------------------------

    def _format_batch(self, batch: list[dict]) -> str:
        lines: list[str] = []
        for idx, q in enumerate(batch, start=1):
            level = q.get("level", "")
            qtype = q.get("question_type", "")
            lines.append(f"[Câu {idx}] Level: {level} | Loại: {qtype}")
            lines.append(q.get("question_text", ""))
            lines.append(f"A. {q.get('option_a', '')}")
            lines.append(f"B. {q.get('option_b', '')}")
            lines.append(f"C. {q.get('option_c', '')}")
            lines.append(f"D. {q.get('option_d', '')}")
            if q.get("passage"):
                lines.append(f"[Đoạn văn]: {q['passage'][:300]}")
            lines.append("")
        return "\n".join(lines)

    # ------------------------------------------------------------------

    def _parse_response(self, raw: str, expected: int) -> list[dict[str, str]]:
        # Strip possible markdown code fences
        text = raw
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
            text = text.rsplit("```", 1)[0]
        text = text.strip()

        try:
            data = json.loads(text)
            if isinstance(data, list) and len(data) == expected:
                return [
                    {
                        "answer": str(item.get("answer", "A")).upper(),
                        "explanation": str(item.get("explanation", "")),
                    }
                    for item in data
                ]
            logger.warning(
                "[ai_answerer] expected %d answers, got %d — padding/trimming",
                expected, len(data) if isinstance(data, list) else 0,
            )
            if isinstance(data, list):
                # Pad or trim to match
                while len(data) < expected:
                    data.append({"answer": "A", "explanation": ""})
                return [
                    {
                        "answer": str(item.get("answer", "A")).upper(),
                        "explanation": str(item.get("explanation", "")),
                    }
                    for item in data[:expected]
                ]
        except json.JSONDecodeError as exc:
            logger.error("[ai_answerer] JSON parse error: %s | raw: %.200s", exc, raw)

        return [{"answer": "A", "explanation": ""} for _ in range(expected)]
