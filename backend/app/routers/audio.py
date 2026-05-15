"""
API endpoint tạo audio on-demand cho câu nghe hiểu JLPT.

POST /audio-api/generate
  - Nhận text + question_id
  - Kiểm tra cache (file đã tồn tại)
  - Gọi edge-tts tạo MP3 nếu chưa có
  - Cập nhật audio_url + is_active=True trong DB
  - Trả về {audio_url, cached}
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import ssl
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Question

router = APIRouter(tags=["audio"])

_HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.normpath(os.path.join(_HERE, "..", "..", "..", "static", "audio"))
VOICE_DEFAULT = "ja-JP-NanamiNeural"


class AudioGenerateRequest(BaseModel):
    text: str
    question_id: int
    voice: str = VOICE_DEFAULT


class AudioGenerateResponse(BaseModel):
    audio_url: str
    cached: bool


def _audio_filename(text: str) -> str:
    h = hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]
    return f"jlpt_{h}.mp3"


async def _tts(text: str, voice: str, out_path: str) -> None:
    try:
        import edge_tts
        import edge_tts.communicate as _ec

        # Bypass proxy SSL certificate verification
        _ctx = ssl.create_default_context()
        _ctx.check_hostname = False
        _ctx.verify_mode = ssl.CERT_NONE
        _ec._SSL_CTX = _ctx

        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(out_path)
    except ImportError:
        raise RuntimeError("edge-tts chưa được cài đặt. Chạy: pip install edge-tts")


@router.post("/generate", response_model=AudioGenerateResponse)
async def generate_audio(payload: AudioGenerateRequest, db: Session = Depends(get_db)):
    """Tạo file audio MP3 từ text bằng edge-tts, trả về URL để phát."""
    os.makedirs(AUDIO_DIR, exist_ok=True)

    filename = _audio_filename(payload.text)
    out_path = os.path.join(AUDIO_DIR, filename)
    audio_url = f"/audio/{filename}"

    cached = os.path.exists(out_path)

    if not cached:
        try:
            await _tts(payload.text, payload.voice, out_path)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Không thể tạo audio: {e}",
            )

    # Cập nhật DB: gắn audio_url và kích hoạt câu hỏi
    question = db.get(Question, payload.question_id)
    if question and (not question.audio_url or not question.is_active):
        question.audio_url = audio_url
        question.is_active = True
        db.commit()

    return AudioGenerateResponse(audio_url=audio_url, cached=cached)
