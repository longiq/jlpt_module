#!/bin/bash
# JLPT Question Bank - Start Server

cd "$(dirname "$0")"

echo "=== JLPT 問題バンク ==="
echo "Installing dependencies..."
pip install -q fastapi uvicorn[standard] sqlalchemy pydantic requests beautifulsoup4 lxml python-multipart aiofiles

echo "Starting server at http://localhost:8000 ..."
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
