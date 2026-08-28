from app.main import app

# Vercel's Python runtime looks for a variable named `app` (ASGI/WSGI
# app) in this file when using the @vercel/python builder pointed at
# api/index.py. This just re-exports the real FastAPI app.
