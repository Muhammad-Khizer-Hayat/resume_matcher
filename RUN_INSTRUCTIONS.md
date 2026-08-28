# Resume Matcher — Run Instructions

One backend (FastAPI) that also serves the frontend directly. Run one
command, get one URL, open it in your browser — that's the whole app.

## Setup (do this once)

Open a terminal in the project root, then:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a file named `.env` inside `backend/` (copy `.env.example` and fill
it in with a real key):

```
GROQ_API_KEY=your_actual_groq_api_key
FRONTEND_ORIGIN=*
```

Get a free key at https://console.groq.com/keys if you don't have one.

## Run it

Every time you want to use the app, from `backend/` (with the venv
activated):

```powershell
uvicorn app.main:app --reload
```

You'll see:

```
Uvicorn running on http://127.0.0.1:8000
```

Copy that URL — **http://127.0.0.1:8000** — and open it in your browser.
That's it: the website itself loads there, not just an API response.

The first request you submit will take a bit longer than usual — it
downloads a small (~80MB) local embedding model from Hugging Face the
first time it's used, then caches it for every request after that.

## Using it

1. Upload a résumé (PDF, DOCX, or TXT).
2. Fill in the job title and paste the job description.
3. Click **Run Match** — the results panel fills in with the score gauge,
   sub-score breakdown, matched/missing skills, and an AI-written summary.

## Troubleshooting

- **Browser shows `{"detail":"Not Found"}` or raw JSON at the URL** —
  you're running an older version of `app/main.py` that doesn't serve the
  frontend. Make sure `backend/app/main.py` mounts `StaticFiles` at `/`
  (see the file in this zip).
- **`GROQ_API_KEY environment variable is not set`** — the `.env` file is
  missing, misnamed, or not directly inside `backend/`.
- **`Invalid API Key`** — the key in `.env` is wrong or revoked; generate a
  fresh one from the Groq console.
- **Nothing happens when you click Run Match / console shows a fetch
  error** — the backend terminal isn't running, or crashed. Check that
  terminal for errors.

