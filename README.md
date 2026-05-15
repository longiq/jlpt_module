# JLPT 問題バンク — Ngân hàng câu hỏi JLPT

Ứng dụng luyện thi JLPT (N1–N5) toàn diện: ngân hàng 540+ câu hỏi, chế độ luyện tập nhanh, thi thử đầy đủ theo cấu trúc đề thật, hỗ trợ câu nghe hiểu với TTS on-demand.

---

## Mục lục

1. [Tính năng](#tính-năng)
2. [Cấu trúc đề thi JLPT](#cấu-trúc-đề-thi-jlpt)
3. [Kiến trúc hệ thống](#kiến-trúc-hệ-thống)
4. [Cấu trúc dự án](#cấu-trúc-dự-án)
5. [Cài đặt & Chạy](#cài-đặt--chạy)
6. [API Endpoints](#api-endpoints)
7. [Dữ liệu mẫu (Seed Data)](#dữ-liệu-mẫu-seed-data)
8. [Hệ thống câu nghe hiểu](#hệ-thống-câu-nghe-hiểu)
9. [Lưu trữ media (Audio & Ảnh)](#lưu-trữ-media-audio--ảnh)
10. [Tạo audio TTS](#tạo-audio-tts)
11. [Trạng thái câu hỏi (is_active)](#trạng-thái-câu-hỏi-is_active)
12. [Scale & Maintain](#scale--maintain)

---

## Tính năng

| Tính năng | Mô tả |
|-----------|-------|
| **540+ câu hỏi** | N1–N5 × 4 loại: từ vựng, ngữ pháp, đọc hiểu, nghe hiểu |
| **Luyện tập nhanh** | Chọn cấp độ + loại đề + số câu, làm bài không giới hạn thời gian |
| **Thi thử đầy đủ** | Đúng số câu và thời gian theo đề thi JLPT thật |
| **Xáo trộn thông minh** | Câu hỏi và đáp án được xáo ngẫu nhiên mỗi lần thi |
| **Timer đếm ngược** | Thi thử có đồng hồ đếm ngược, cảnh báo khi gần hết giờ |
| **Câu nghe hiểu** | Audio player đầy đủ (seek bar), TTS tự động theo yêu cầu |
| **Toggle passage** | Ẩn/hiện nội dung nghe hiểu để luyện kỹ năng nghe thật |
| **Thống kê chi tiết** | Xem số câu theo từng cấp và từng loại đề |
| **API REST** | FastAPI với Swagger UI tại `/docs` |
| **Seed tự động** | Dữ liệu mẫu được nạp mỗi khi server khởi động |

---

## Cấu trúc đề thi JLPT

Chế độ **Thi thử đầy đủ** sử dụng đúng số câu theo tiêu chuẩn đề thi thật:

| Cấp độ | Từ vựng | Ngữ pháp | Đọc hiểu | Nghe hiểu | Thời gian |
|--------|---------|----------|----------|-----------|-----------|
| N5 | 25 | 16 | 9 | 12 | 105 phút |
| N4 | 25 | 16 | 12 | 14 | 115 phút |
| N3 | 25 | 24 | 19 | 22 | 140 phút |
| N2 | 28 | 12 | 32 | 29 | 155 phút |
| N1 | 25 | 10 | 34 | 29 | 170 phút |

> Trong chế độ thi thử, câu nghe hiểu chỉ xuất hiện nếu `is_active=True` (đã có file audio).

---

## Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (HTML/CSS/JS)               │
│  index.html  ←  /css/style.css  ←  /js/app.js           │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP / REST API
┌───────────────────────▼─────────────────────────────────┐
│                   FastAPI Backend                        │
│                                                         │
│  /questions   → questions.py   (CRUD, stats)            │
│  /quiz        → quiz.py        (session, answer, score) │
│  /crawler     → crawler.py     (crawl từ website)       │
│  /audio-api   → audio.py       (TTS on-demand)          │
│                                                         │
│  /audio/*     → static/audio/  (file MP3)               │
│  /images/*    → static/images/ (file ảnh)               │
│  /css/*       → frontend/css/                           │
│  /js/*        → frontend/js/                            │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│              SQLite Database (data/questions.db)         │
│  Table: questions, quiz_sessions, quiz_answers           │
└─────────────────────────────────────────────────────────┘
```

**Stack:**
- Backend: Python 3.10+, FastAPI, SQLAlchemy ORM, Pydantic v2, SQLite
- Frontend: Vanilla HTML/CSS/JavaScript (không dùng framework)
- TTS: Microsoft edge-tts (`ja-JP-NanamiNeural`, `ja-JP-KeitaNeural`)
- Serving: Uvicorn (dev), có thể dùng Gunicorn + Nginx (production)

---

## Cấu trúc dự án

```
jlpt_module/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, startup migration, static mounts
│   │   ├── models.py            # SQLAlchemy models (Question, QuizSession, QuizAnswer)
│   │   ├── schemas.py           # Pydantic v2 schemas
│   │   ├── database.py          # SQLite engine + SessionLocal
│   │   └── routers/
│   │       ├── questions.py     # GET/POST/PATCH /questions, stats
│   │       ├── quiz.py          # POST /quiz/start, /quiz/{id}/answer, /quiz/{id}/score
│   │       ├── crawler.py       # POST /crawler/crawl
│   │       └── audio.py         # POST /audio-api/generate (TTS on-demand)
│   └── crawler/
│       ├── seed_data.py             # Entry point: gộp tất cả seed files
│       ├── seed_data_n5_n4.py       # 160 câu N5+N4
│       ├── seed_data_n3.py          # 90 câu N3
│       ├── seed_data_n2.py          # 103 câu N2
│       ├── seed_data_n1.py          # 83 câu N1
│       └── seed_data_listening_demo.py  # 4 câu nghe hiểu demo có ảnh SVG
├── frontend/
│   ├── index.html               # SPA duy nhất
│   ├── css/style.css            # Toàn bộ CSS
│   └── js/app.js                # Toàn bộ logic frontend
├── scripts/
│   └── generate_audio.py        # CLI batch TTS (cần internet thật)
├── static/                      # Media files — KHÔNG commit vào git
│   ├── audio/                   # File MP3 (tạo bởi TTS)
│   │   └── .gitkeep
│   └── images/                  # File ảnh
│       └── .gitkeep
├── data/                        # SQLite DB — KHÔNG commit vào git
│   └── questions.db
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Cài đặt & Chạy

### Yêu cầu

- Python 3.10+
- pip

### Cài đặt

```bash
git clone https://github.com/longiq/jlpt_module.git
cd jlpt_module
pip install -r requirements.txt
```

### Khởi động server

```bash
# Development (auto-reload)
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

# Production
gunicorn backend.app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

Mở trình duyệt: **http://localhost:8000**

API Docs (Swagger): **http://localhost:8000/docs**

### Khởi động lần đầu

Khi server start, `on_startup()` trong `main.py` tự động:

1. Tạo thư mục `data/` nếu chưa có
2. Tạo tất cả các bảng DB (`Base.metadata.create_all`)
3. **Migration tự động**: thêm cột `image_url`, `is_active` vào bảng `questions` nếu chưa có (backward-compatible)
4. Đánh dấu `is_active=False` cho các câu nghe hiểu không có audio
5. **Nạp seed data**: thêm câu hỏi còn thiếu (bỏ qua câu đã tồn tại theo `level + question_text`)

---

## API Endpoints

### Questions

| Method | Path | Mô tả |
|--------|------|-------|
| `GET` | `/questions/` | Lấy danh sách câu hỏi (lọc theo level, type, limit) |
| `POST` | `/questions/` | Thêm câu hỏi mới |
| `PATCH` | `/questions/{id}` | Cập nhật câu hỏi |
| `DELETE` | `/questions/{id}` | Xóa câu hỏi |
| `GET` | `/questions/stats` | Thống kê tổng số câu theo cấp độ và loại |

**Stats response mẫu:**
```json
{
  "total": 540,
  "by_level": {"N5": 101, "N4": 102},
  "by_level_type": {
    "N5": {"vocabulary": 38, "grammar": 38, "reading": 14, "listening": 11}
  }
}
```

### Quiz

| Method | Path | Mô tả |
|--------|------|-------|
| `POST` | `/quiz/start` | Bắt đầu phiên quiz mới |
| `POST` | `/quiz/{id}/answer` | Trả lời 1 câu |
| `GET` | `/quiz/{id}/score` | Lấy kết quả phiên quiz |
| `GET` | `/quiz/history` | Lịch sử các lần thi |

**Quiz start request:**
```json
{
  "level": "N3",
  "question_type": "all",
  "num_questions": 20,
  "full_exam": false
}
```

Khi `full_exam: true`, `level` bắt buộc phải chỉ định và hệ thống tự chọn đúng số câu theo `JLPT_STRUCTURE`.

### Audio (TTS on-demand)

| Method | Path | Mô tả |
|--------|------|-------|
| `POST` | `/audio-api/generate` | Tạo file MP3 từ text, trả về URL |

**Request:**
```json
{
  "text": "会議は何時に始まりますか。",
  "question_id": 42,
  "voice": "ja-JP-NanamiNeural"
}
```

**Response:**
```json
{
  "audio_url": "/audio/jlpt_a3f2b1c4d5e6f7a8.mp3",
  "cached": false
}
```

Giọng đọc có thể dùng:
- `ja-JP-NanamiNeural` — giọng nữ (mặc định)
- `ja-JP-KeitaNeural` — giọng nam (hội thoại)

### Crawler

| Method | Path | Mô tả |
|--------|------|-------|
| `POST` | `/crawler/crawl` | Crawl câu hỏi từ URL cho trước |

---

## Dữ liệu mẫu (Seed Data)

### Tổng quan

| File | Nội dung | Số câu |
|------|----------|--------|
| `seed_data.py` | Entry point + câu gốc N5 (vocab/grammar/reading) | ~20 câu base |
| `seed_data_n5_n4.py` | N5+N4: vocab, grammar, reading, listening | 160 câu |
| `seed_data_n3.py` | N3: vocab, grammar, reading, listening | 90 câu |
| `seed_data_n2.py` | N2: vocab, grammar, reading, listening | 103 câu |
| `seed_data_n1.py` | N1: vocab, grammar, reading, listening | 83 câu |
| `seed_data_listening_demo.py` | Demo nghe hiểu có ảnh SVG minh họa | 4 câu |
| **Tổng** | | **~540 câu** |

### Phân bổ hiện tại

| Cấp độ | Từ vựng | Ngữ pháp | Đọc hiểu | Nghe hiểu | Tổng |
|--------|---------|----------|----------|-----------|------|
| N5 | 38 | 38 | 14 | 11 | 101 |
| N4 | 38 | 38 | 14 | 12 | 102 |
| N3 | 38 | 38 | 19 | 16 | 111 |
| N2 | 43 | 33 | 29 | 18 | 123 |
| N1 | 36 | 30 | 24 | 13 | 103 |
| **Tổng** | **193** | **177** | **100** | **70** | **540** |

### Cấu trúc 1 câu hỏi

```python
{
    "level": "N3",                    # N1 | N2 | N3 | N4 | N5
    "question_type": "listening",     # vocabulary | grammar | reading | listening
    "passage": "田中さんは...",         # Đoạn văn (optional, dùng cho reading/listening)
    "question_text": "田中さんは何をしますか？",
    "option_a": "映画を見ます",
    "option_b": "料理をします",
    "option_c": "本を読みます",
    "option_d": "音楽を聞きます",
    "correct_answer": "A",
    "explanation": "Giải thích...",
    "audio_url": None,                # "/audio/jlpt_xxx.mp3" khi đã tạo
    "image_url": None,                # URL ảnh hoặc data URI (SVG)
    "is_active": False,               # False cho câu nghe hiểu chưa có audio
}
```

### Thêm seed data mới

Tạo file `backend/crawler/seed_data_<tên>.py` với hàm `get_<tên>_questions() -> list[dict]`, sau đó import trong `seed_data.py`:

```python
# seed_data.py
try:
    from .seed_data_xxx import get_xxx_questions
    extended += get_xxx_questions()
except ImportError:
    pass
```

Server sẽ tự nạp khi khởi động lại.

---

## Hệ thống câu nghe hiểu

### Luồng hoạt động

```
User click "🎧 Nghe và xem nội dung"
    │
    ├─ Câu đã có audio_url? → Hiển thị audio player ngay
    │
    └─ Chưa có → POST /audio-api/generate
                    │
                    ├─ File MP3 đã tồn tại? → Trả về URL (cached=true)
                    │
                    └─ Chưa có → Gọi edge-tts → Lưu MP3
                                  → Cập nhật DB (audio_url, is_active=True)
                                  → Trả về URL

    → Frontend render <audio controls autoplay>
    → Hiện passage text (có thể ẩn/hiện bằng nút toggle)
```

### Ảnh minh họa

Câu nghe hiểu có thể đi kèm ảnh minh họa qua trường `image_url`:
- File thật: `"/images/n3_listening_01.png"` (lưu tại `static/images/`)
- Inline SVG: `"data:image/svg+xml;base64,..."` (dùng cho seed data demo)

Ảnh luôn hiển thị phía trên nút audio, không bị ẩn/hiện.

---

## Lưu trữ media (Audio & Ảnh)

### Chiến lược

Media (MP3, ảnh) **không được commit vào git** để tránh repo nặng:

| Loại | Thư mục | Git | Tạo bằng |
|------|---------|-----|----------|
| Audio MP3 | `static/audio/` | `.gitignore` | edge-tts (TTS API) |
| Ảnh | `static/images/` | `.gitignore` | Tải thủ công / crawl |

Chỉ có `.gitkeep` trong mỗi thư mục để git track thư mục rỗng.

FastAPI serve trực tiếp:
```python
app.mount("/audio",  StaticFiles(directory="static/audio"),  name="audio")
app.mount("/images", StaticFiles(directory="static/images"), name="images")
```

### Production: CDN hoặc object storage

Khi scale lên production, thay `static/audio/` bằng:
- **AWS S3 + CloudFront**: Upload MP3 lên S3, `audio_url` = CloudFront URL
- **Cloudflare R2**: Tương tự S3, không mất phí egress
- **Self-hosted MinIO**: Object storage tự host

Chỉ cần thay đổi `audio_url` trong DB và logic ghi file trong `audio.py`.

---

## Tạo audio TTS

### Cách 1: On-demand qua API (khuyến nghị)

Người dùng click nút trong quiz → backend tự tạo → lưu cache → trả URL.
Không cần cấu hình thêm gì, hoạt động tự động khi server có internet.

### Cách 2: Batch tạo trước bằng script

```bash
# Xem danh sách sẽ tạo (không tạo file thật)
python3 scripts/generate_audio.py --dry-run

# Tạo audio cho N5 + cập nhật DB
python3 scripts/generate_audio.py --level N5 --db

# Tạo audio tất cả cấp độ + cập nhật DB
python3 scripts/generate_audio.py --level all --db
```

Cờ `--db` tự cập nhật `audio_url` và `is_active=True` trong database sau khi tạo xong.

### Yêu cầu

- `pip install edge-tts` (đã có trong `requirements.txt`)
- Kết nối internet thật đến `speech.platform.bing.com`
- Không hoạt động sau proxy SSL-inspection của doanh nghiệp

### Giọng đọc

| Giọng | Dùng cho |
|-------|----------|
| `ja-JP-NanamiNeural` | Passage, câu hỏi (giọng nữ, mặc định) |
| `ja-JP-KeitaNeural` | Hội thoại nam trong đoạn nghe |

### Lưu ý môi trường proxy

Trong môi trường có proxy SSL-inspection, edge-tts sẽ báo lỗi SSL hoặc 403 từ Microsoft (proxy sửa WebSocket headers). Khi đó:
- Endpoint `/audio-api/generate` trả về HTTP 503 với thông báo lỗi rõ ràng
- Chạy `generate_audio.py` trên server có internet thật, sau đó copy file MP3 vào `static/audio/`

---

## Trạng thái câu hỏi (is_active)

Trường `is_active` (`Boolean`, mặc định `True`) kiểm soát câu hỏi có xuất hiện trong quiz không.

### Quy tắc

| Trạng thái | Câu nào | Lý do |
|-----------|---------|-------|
| `is_active=False` | Câu nghe hiểu không có `audio_url` | Nghe hiểu bắt buộc phải có audio |
| `is_active=True` | Tất cả câu còn lại | Mặc định |

### Tự động cập nhật

- **Startup**: server tự đánh dấu `is_active=0` cho câu nghe hiểu không có audio
- **Sau TTS thành công**: `is_active` tự chuyển thành `True`, câu xuất hiện trong quiz ngay
- **Script batch**: `generate_audio.py --db` cập nhật hàng loạt

### Migration backward-compatible

Khi upgrade từ version cũ (chưa có cột `is_active`), server tự chạy:

```sql
ALTER TABLE questions ADD COLUMN is_active INTEGER DEFAULT 1;
ALTER TABLE questions ADD COLUMN image_url TEXT;
UPDATE questions SET is_active = 0
  WHERE question_type = 'listening' AND (audio_url IS NULL OR audio_url = '');
```

Dữ liệu cũ được giữ nguyên, không cần xóa DB.

---

## Scale & Maintain

### Thêm câu hỏi

1. Tạo file `backend/crawler/seed_data_<tên>.py`
2. Định nghĩa `get_<tên>_questions() -> list[dict]`
3. Import trong `seed_data.py` (trong `try/except ImportError`)
4. Restart server → câu mới tự được nạp

### Thêm cấp độ hoặc loại đề

1. Cập nhật `JLPT_STRUCTURE` trong `backend/app/routers/quiz.py`
2. Cập nhật `LEVELS` và `TYPES` trong `backend/app/routers/questions.py`
3. Thêm seed data tương ứng

### Thêm câu nghe hiểu

1. Thêm vào seed data với `is_active: False` và `audio_url: None`
2. Chạy `python3 scripts/generate_audio.py --db` hoặc để người dùng trigger on-demand
3. Câu tự `is_active=True` sau khi có audio

### Crawler tự động

Dùng endpoint `POST /crawler/crawl` để thu thập câu hỏi từ website:

```bash
curl -X POST http://localhost:8000/crawler/crawl \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/jlpt-n3", "level": "N3"}'
```

### Database

SQLite phù hợp cho ~10,000 câu hỏi và lưu lượng truy cập nhỏ.
Khi cần scale:
1. Chuyển sang PostgreSQL: chỉ đổi `DATABASE_URL` trong `database.py`
2. Mọi ORM query trong routers tương thích hoàn toàn (không cần sửa thêm)

### Backup

```bash
# Backup DB
cp data/questions.db data/questions.db.backup

# Backup audio
tar -czf audio_backup.tar.gz static/audio/
```

### Biến môi trường (production)

Tạo `.env` (không commit vào git):
```env
DATABASE_URL=sqlite:///./data/questions.db
# Hoặc PostgreSQL:
# DATABASE_URL=postgresql://user:pass@localhost/jlpt_db
```

---

## Đóng góp & Phát triển

- Branch chính: `main`
- Feature branches: `claude/feature-name`
- Seed data mới: thêm file riêng, không sửa trực tiếp `seed_data.py` trừ khi cần thay đổi entry point
- Không commit file media (`static/audio/`, `static/images/`, `data/`)
