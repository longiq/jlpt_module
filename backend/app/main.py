import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func

from .database import SessionLocal, engine
from .models import Base, Question
from .routers import questions, quiz
from .routers import crawler as crawler_router_module
from .routers import audio as audio_router_module

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))

# backend/app/main.py  →  ../../frontend  →  <project_root>/frontend
FRONTEND_DIR = os.path.normpath(os.path.join(_HERE, "..", "..", "frontend"))

# <project_root>/data
DATA_DIR = os.path.normpath(os.path.join(_HERE, "..", "..", "data"))

# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="JLPT Question Bank API",
    description="Backend API for the JLPT quiz application.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS — allow all origins (suitable for development; restrict in production)
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(questions.router, prefix="/questions")
app.include_router(quiz.router, prefix="/quiz")
app.include_router(crawler_router_module.router, prefix="/crawler")
app.include_router(audio_router_module.router, prefix="/audio-api")

# ---------------------------------------------------------------------------
# Startup: create DB tables, optionally seed data
# ---------------------------------------------------------------------------

@app.on_event("startup")
def on_startup() -> None:
    # Ensure the data/ directory exists before SQLAlchemy tries to open the DB
    os.makedirs(DATA_DIR, exist_ok=True)

    # Create all declared tables (no-op if they already exist)
    Base.metadata.create_all(bind=engine)

    # Migrate: add new nullable columns to existing tables if missing
    from sqlalchemy import text as _text
    with engine.connect() as conn:
        for col, col_type in [("image_url", "TEXT"), ("is_active", "INTEGER DEFAULT 1")]:
            try:
                conn.execute(_text(f"ALTER TABLE questions ADD COLUMN {col} {col_type}"))
                conn.commit()
                print(f"[migration] Added column questions.{col}")
            except Exception:
                pass  # column already exists

        # Deactivate text-only listening questions (no audio)
        result = conn.execute(_text(
            "UPDATE questions SET is_active = 0 "
            "WHERE question_type = 'listening' AND (audio_url IS NULL OR audio_url = '')"
        ))
        conn.commit()
        if result.rowcount:
            print(f"[migration] Deactivated {result.rowcount} text-only listening question(s)")

    # Always sync seed questions on startup (insert missing, skip duplicates)
    db = SessionLocal()
    try:
        try:
            try:
                from backend.crawler.seed_data import get_seed_questions
            except ImportError:
                from ..crawler.seed_data import get_seed_questions  # type: ignore[import]

            questions = get_seed_questions()
            added = 0
            for q in questions:
                exists = (
                    db.query(Question)
                    .filter(
                        Question.level == q["level"],
                        Question.question_text == q["question_text"],
                    )
                    .first()
                )
                if not exists:
                    db.add(Question(**q))
                    added += 1
            if added:
                db.commit()
                print(f"[startup] Seeded {added} new question(s).")
            else:
                print("[startup] Seed data already up to date.")
        except Exception as e:
            print(f"[startup] Seed skipped: {e}")
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Serve media static files (audio / images) — not tracked in git
# ---------------------------------------------------------------------------
_STATIC_DIR = os.path.normpath(os.path.join(_HERE, "..", "..", "static"))
for _subdir, _mount in [("audio", "/audio"), ("images", "/images")]:
    _media_dir = os.path.join(_STATIC_DIR, _subdir)
    os.makedirs(_media_dir, exist_ok=True)
    app.mount(_mount, StaticFiles(directory=_media_dir), name=_subdir)

# ---------------------------------------------------------------------------
# Serve frontend static files (if the frontend directory exists)
# Mount /css and /js explicitly so API routes (/questions, /quiz, /crawler)
# are not shadowed by a root-level StaticFiles mount.
# ---------------------------------------------------------------------------
if os.path.isdir(FRONTEND_DIR):
    _css_dir = os.path.join(FRONTEND_DIR, "css")
    _js_dir = os.path.join(FRONTEND_DIR, "js")

    if os.path.isdir(_css_dir):
        app.mount("/css", StaticFiles(directory=_css_dir), name="css")
    if os.path.isdir(_js_dir):
        app.mount("/js", StaticFiles(directory=_js_dir), name="js")

    @app.get("/", include_in_schema=False)
    def serve_index() -> FileResponse:
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
else:
    @app.get("/", include_in_schema=False)
    def root() -> dict:
        return {"message": "JLPT Question Bank API is running."}
