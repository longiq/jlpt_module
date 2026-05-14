# JLPT 問題バンク (JLPT Question Bank)

Ứng dụng luyện thi JLPT (N1–N5) với ngân hàng câu hỏi, crawler tự động và giao diện quiz có tính giờ.

## Tính năng

- **Ngân hàng câu hỏi**: 100+ câu mẫu N1–N5 (語彙・文法・読解) tích hợp sẵn
- **Crawler tự động**: thu thập câu hỏi từ các trang học tiếng Nhật (ví dụ: dethitiengnhat.com)
- **Xáo trộn thông minh**: thứ tự câu hỏi và thứ tự đáp án được xáo ngẫu nhiên mỗi lần thi
- **Giao diện quiz**: timer đếm ngược, chấm điểm, hiển thị giải thích sau mỗi câu
- **Lịch sử**: xem lại kết quả các lần thi trước
- **API REST**: FastAPI với Swagger UI tại `/docs`

## Cấu trúc đề thi JLPT

| Cấp độ | 語彙 | 文法・読解 | 聴解 | Điểm đạt |
|--------|------|-----------|------|----------|
| N5 | 25 phút | 50 phút | 30 phút | 80/180 |
| N4 | 25 phút | 55 phút | 35 phút | 90/180 |
| N3 | 30 phút | 70 phút | 40 phút | 95/180 |
| N2 | 105 phút | — | 50 phút | 90/180 |
| N1 | 110 phút | — | 60 phút | 100/180 |

## Cài đặt & Chạy

```bash
# Cài dependencies
pip install -r requirements.txt

# Khởi động server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

# Hoặc dùng script
./start.sh
```

Mở trình duyệt: http://localhost:8000

## Cấu trúc dự án

```
jlpt_module/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app
│   │   ├── models.py        # SQLAlchemy models (Question, QuizSession, QuizAnswer)
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── database.py      # SQLite setup
│   │   └── routers/
│   │       ├── questions.py # CRUD API cho câu hỏi
│   │       ├── quiz.py      # Quiz session API
│   │       └── crawler.py   # Trigger crawler API
│   └── crawler/
│       ├── base.py              # Base crawler class
│       ├── dethitiengnhat.py    # Crawler cho dethitiengnhat.com
│       └── seed_data.py         # 100 câu hỏi mẫu N1-N5
├── frontend/
│   ├── index.html           # SPA chính
│   ├── css/style.css
│   └── js/app.js
├── data/                    # SQLite database (auto-created)
├── requirements.txt
└── start.sh
```

## API Endpoints

| Method | Path | Mô tả |
|--------|------|-------|
| `GET` | `/questions/stats/summary` | Thống kê số câu theo cấp độ/loại |
| `POST` | `/quiz/start` | Bắt đầu quiz (chọn level, type, số câu) |
| `POST` | `/quiz/{id}/answer` | Nộp đáp án 1 câu |
| `POST` | `/quiz/{id}/complete` | Kết thúc quiz, lấy điểm |
| `GET` | `/quiz/history` | Lịch sử các lần thi |
| `POST` | `/crawler/seed` | Nạp dữ liệu mẫu |
| `POST` | `/crawler/run` | Chạy crawler |

Swagger UI: http://localhost:8000/docs

## Lưu ý về Crawler

Website dethitiengnhat.com có cơ chế chặn crawler (HTTP 403). Ứng dụng đã được trang bị:
- Browser-like headers để vượt qua basic blocking
- Rate limiting (delay giữa các request)
- Fallback sang 100 câu hỏi mẫu tích hợp sẵn

Nếu crawler thất bại, dùng nút **"サンプルデータを読み込む"** trong trang Admin để nạp dữ liệu mẫu.
