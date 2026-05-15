"""
Tạo file audio (.mp3) cho các câu nghe hiểu JLPT bằng edge-tts.

Cách dùng:
  python3 scripts/generate_audio.py [--level N5] [--dry-run] [--db]

Tùy chọn:
  --level N5|N4|N3|N2|N1|all   Chỉ tạo audio cho cấp độ này (mặc định: all)
  --dry-run                     Chỉ in danh sách, không tạo file
  --db                          Cập nhật audio_url và is_active vào DB sau khi tạo

Giọng đọc:
  Hội thoại nam: ja-JP-KeitaNeural
  Hội thoại nữ: ja-JP-NanamiNeural  (mặc định cho passage)
  Câu hỏi:      ja-JP-NanamiNeural
"""

import argparse
import asyncio
import hashlib
import os
import sys

# Thêm thư mục gốc vào path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

AUDIO_DIR = os.path.join(ROOT, "static", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

VOICE_PASSAGE = "ja-JP-NanamiNeural"
VOICE_QUESTION = "ja-JP-NanamiNeural"


def _audio_filename(text: str) -> str:
    """Tạo tên file từ hash SHA1 của nội dung."""
    h = hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]
    return f"jlpt_{h}.mp3"


async def _generate_one(text: str, voice: str, out_path: str) -> None:
    import edge_tts
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(out_path)


async def generate_audio_for_question(q: dict, dry_run: bool) -> str | None:
    """Tạo file audio cho 1 câu, trả về audio_url (/audio/filename.mp3) hoặc None."""
    passage = (q.get("passage") or "").strip()
    question_text = (q.get("question_text") or "").strip()

    if not passage and not question_text:
        return None

    # Ghép nội dung: passage + ngắt + câu hỏi
    full_text = passage
    if question_text:
        full_text = f"{passage}\n\n{question_text}" if passage else question_text

    filename = _audio_filename(full_text)
    out_path = os.path.join(AUDIO_DIR, filename)
    audio_url = f"/audio/{filename}"

    if dry_run:
        print(f"  [dry-run] {filename} ← {full_text[:60]}...")
        return audio_url

    if os.path.exists(out_path):
        print(f"  [skip] {filename} đã tồn tại")
        return audio_url

    try:
        await _generate_one(full_text, VOICE_PASSAGE, out_path)
        size_kb = os.path.getsize(out_path) // 1024
        print(f"  [ok] {filename} ({size_kb} KB)")
        return audio_url
    except Exception as e:
        print(f"  [lỗi] {e}")
        return None


async def main(level_filter: str, dry_run: bool, update_db: bool) -> None:
    from backend.crawler.seed_data import get_seed_questions

    questions = [
        q for q in get_seed_questions()
        if q["question_type"] == "listening"
        and (level_filter == "all" or q["level"] == level_filter)
    ]

    print(f"Tìm thấy {len(questions)} câu nghe hiểu (level={level_filter})")
    if dry_run:
        print("--- CHẾ ĐỘ DRY-RUN ---")

    results: list[tuple[dict, str]] = []  # (question, audio_url)

    for i, q in enumerate(questions, 1):
        print(f"\n[{i}/{len(questions)}] {q['level']} — {q['question_text'][:50]}")
        url = await generate_audio_for_question(q, dry_run)
        if url:
            results.append((q, url))

    print(f"\n✓ Đã tạo/xác nhận {len(results)} file audio")

    if update_db and results and not dry_run:
        _update_database(results)


def _update_database(results: list[tuple[dict, str]]) -> None:
    """Cập nhật audio_url và is_active=True trong DB."""
    from backend.app.database import SessionLocal
    from backend.app.models import Question

    db = SessionLocal()
    try:
        updated = 0
        for q, audio_url in results:
            row = (
                db.query(Question)
                .filter(
                    Question.level == q["level"],
                    Question.question_text == q["question_text"],
                )
                .first()
            )
            if row:
                row.audio_url = audio_url
                row.is_active = True
                updated += 1
        db.commit()
        print(f"[DB] Đã cập nhật {updated} câu hỏi (audio_url + is_active=True)")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tạo audio cho câu nghe hiểu JLPT")
    parser.add_argument("--level", default="all", help="N5|N4|N3|N2|N1|all")
    parser.add_argument("--dry-run", action="store_true", help="Chỉ in, không tạo file")
    parser.add_argument("--db", action="store_true", help="Cập nhật DB sau khi tạo")
    args = parser.parse_args()

    asyncio.run(main(args.level, args.dry_run, args.db))
