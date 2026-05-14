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

# ---------------------------------------------------------------------------
# Startup: create DB tables, optionally seed data
# ---------------------------------------------------------------------------

@app.on_event("startup")
def on_startup() -> None:
    # Ensure the data/ directory exists before SQLAlchemy tries to open the DB
    os.makedirs(DATA_DIR, exist_ok=True)

    # Create all declared tables (no-op if they already exist)
    Base.metadata.create_all(bind=engine)

    # Seed the database when the questions table is empty
    db = SessionLocal()
    try:
        count: int = db.query(func.count(Question.id)).scalar() or 0
        if count == 0:
            try:
                try:
                    from backend.crawler.seed_data import seed_database
                except ImportError:
                    from ..crawler.seed_data import seed_database  # type: ignore[import]
                seed_database(db)
            except Exception:
                pass  # seed_data not available — skip silently
    finally:
        db.close()


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
