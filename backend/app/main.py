import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import match

app = FastAPI(title="AI Resume Screening & Job Matching API")

# In production, set FRONTEND_ORIGIN to your real frontend URL instead of "*".
allowed_origins = os.environ.get("FRONTEND_ORIGIN", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(match.router, prefix="/api", tags=["matching"])


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "resume-matcher-api"}


# Serve the plain HTML/CSS/JS frontend directly from the backend, so
# visiting the site's root URL shows the actual website instead of just
# the JSON API. This works both locally (uvicorn) and on Vercel — Vercel's
# public/ CDN only auto-serves exact file paths like /style.css, not "/"
# with index.html resolution, so this mount handles that case directly.
frontend_dir = Path(__file__).resolve().parent.parent / "public"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
