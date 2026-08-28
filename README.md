# AI Resume Screening & Job Matching System

## Architecture

- `backend/` — FastAPI service: resume parsing, skill extraction, Groq
  embeddings + semantic similarity, weighted scoring, LLM-generated summary.
  Deploy to **Railway**.
- `frontend/` — React (Vite) upload form + results dashboard.
  Deploy to **Vercel**.

Frontend and backend are deployed separately and talk over HTTPS — this
avoids the Vercel Python serverless bundle-size limits that heavy ML
dependencies (torch, sentence-transformers, faiss) run into.

## Local setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env   # add your GROQ_API_KEY
uvicorn app.main:app --reload
```
Runs on http://localhost:8000. Interactive docs at http://localhost:8000/docs.

### Frontend
```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env.local
npm run dev
```
Runs on http://localhost:5173.

## Deployment

### Backend → Railway
1. Push this repo to GitHub.
2. In Railway: New Project → Deploy from GitHub repo → select `backend/` as
   the root directory (Railway auto-detects the Dockerfile).
3. Add environment variable `GROQ_API_KEY`.
4. After the frontend is deployed, add `FRONTEND_ORIGIN` set to your Vercel
   URL (e.g. `https://your-app.vercel.app`) so CORS isn't wide open.
5. Copy the generated Railway URL (e.g. `https://your-backend.up.railway.app`).

### Frontend → Vercel
1. In Vercel: New Project → import the same GitHub repo → set root directory
   to `frontend/`.
2. Add environment variable `VITE_API_URL` = your Railway backend URL from
   above.
3. Deploy. Vercel auto-detects Vite (`npm run build`, output `dist`).

## Next features to layer on

- Postgres + pgvector for persistent candidate storage and ranked search
  across many candidates (needed for the recruiter dashboard's "rank
  candidates" and "search/filter" features).
- Batch endpoint: match one job description against N resumes at once,
  return a ranked list.
- Auth (recruiter login) before exposing the dashboard publicly.
- Swap the regex-based skill extractor for an LLM extraction pass on
  resumes that don't hit the curated taxonomy well.
