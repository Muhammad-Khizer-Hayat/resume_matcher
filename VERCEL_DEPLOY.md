# Deploying to Vercel (free)

Vercel now supports FastAPI with **zero configuration** — no `vercel.json`
builds/routes needed. It also serves static frontend files from a
`public/` folder automatically, in the same project as the backend. So
this deploys as **one Vercel project**, giving you one URL for both the
UI and the API — same as running it locally.

## 0. One-time accounts needed

- A free Cohere account + API key: https://dashboard.cohere.com/api-keys
- Your existing Groq API key
- A Vercel account (https://vercel.com), connected to your GitHub

## 1. Deploy

1. Go to https://vercel.com/new and import your GitHub repo.
2. Set **Root Directory** to `backend`.
3. Vercel auto-detects FastAPI from `app/main.py` — leave build settings
   as default, no framework preset needed.
4. Before deploying, add Environment Variables (Project Settings →
   Environment Variables):
   - `GROQ_API_KEY` = your Groq key
   - `COHERE_API_KEY` = your Cohere key
5. Click **Deploy**.

## 2. Test it

Open the URL Vercel gives you, e.g. `https://resume-matcher.vercel.app`.
You should see the actual UI — not JSON. Upload a resume, fill in a job
description, and click **Run Match**.

If something fails, open the browser console (F12) for the error, and
check the function logs in the Vercel dashboard (Project → Logs).

## Notes

- Vercel's free tier has a **default 10 second execution timeout** per
  request (configurable up to 60s on Hobby/free via `vercel.json`'s
  `functions` → `maxDuration`, or higher on paid plans). If a request to
  Groq or Cohere is slow, an occasional request may time out — that's a
  hosting limit, not a bug.
- Every `git push` to your connected branch auto-redeploys.
- Local development is unchanged: running `uvicorn app.main:app --reload`
  from `backend/` still serves the whole app (UI included) at
  `http://127.0.0.1:8000`.
- The frontend files live in `backend/public/` now (moved there
  specifically because that's the folder name Vercel looks for to serve
  static files from its CDN automatically).
