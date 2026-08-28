# Deploying to Vercel (free)

Vercel deploys the **frontend** and **backend** as two separate projects
from the same GitHub repo. This is required because Vercel's Python
functions have strict size limits, so the backend can no longer bundle a
local ML model — it now uses Cohere's API for embeddings instead, which
keeps it small enough to deploy for free.

## 0. One-time accounts needed

- A free Cohere account + API key: https://dashboard.cohere.com/api-keys
- Your existing Groq API key
- A Vercel account (https://vercel.com), connected to your GitHub

## 1. Deploy the backend

1. Go to https://vercel.com/new and import your GitHub repo.
2. When asked for the **Root Directory**, set it to `backend`.
3. Vercel should auto-detect the Python runtime from `vercel.json` and
   `requirements.txt`. Leave build/output settings as default.
4. Before deploying, add Environment Variables (Project Settings →
   Environment Variables):
   - `GROQ_API_KEY` = your Groq key
   - `COHERE_API_KEY` = your Cohere key
   - `FRONTEND_ORIGIN` = leave blank for now, you'll set this after step 2
5. Click **Deploy**. Once done, note the URL Vercel gives you, e.g.
   `https://resume-matcher-backend.vercel.app`.
6. Confirm it works by visiting `https://<your-backend-url>/api/health`
   in your browser — you should see
   `{"status":"ok","service":"resume-matcher-api"}`.

## 2. Deploy the frontend

1. Go to https://vercel.com/new again, import the **same repo** as a new
   project.
2. Set **Root Directory** to `frontend`.
3. Framework preset: choose "Other" (it's plain HTML/CSS/JS, no build
   step needed).
4. Before deploying, open `frontend/index.html` in your repo and update
   this line near the bottom to point at your backend URL from step 1:
   ```js
   window.API_URL = "https://resume-matcher-backend.vercel.app";
   ```
   Commit and push this change (Vercel redeploys automatically on push).
5. Click **Deploy**. Note the frontend URL Vercel gives you, e.g.
   `https://resume-matcher.vercel.app`.

## 3. Connect them (CORS)

Go back to the **backend** project on Vercel → Settings → Environment
Variables, and set:

```
FRONTEND_ORIGIN=https://resume-matcher.vercel.app
```

(use your actual frontend URL from step 2). Redeploy the backend for this
to take effect (Deployments tab → "..." on the latest deployment →
Redeploy).

## 4. Test it

Open your frontend URL in the browser, upload a resume, fill in a job
description, and click **Run Match**. If something fails, open the
browser console (F12) for the error, and check the backend's function
logs in the Vercel dashboard (Project → Logs).

## Notes

- Vercel's free tier serverless functions have a **10 second execution
  timeout**. If Groq or Cohere responses are slow, occasional requests
  may time out — this is a hosting limitation, not a bug in the code.
- Every `git push` auto-redeploys both projects.
- Local development is unaffected — running `uvicorn app.main:app
  --reload` from `backend/` still serves the whole app (frontend
  included) at `http://127.0.0.1:8000` exactly as before, since Cohere's
  API is used there too now instead of the local model.
