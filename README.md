# AI Email Marketing Agent

College prototype: LangChain agent + MCP tools + OpenRouter + FastAPI + React + MySQL.

## Features

- Upload CSV contact datasets
- LangChain agent with MCP tools (datasets, subject, **preview text**, HTML/plain body, campaign, send)
- Agent instructions live in `backend/app/agent/system_prompt.py` (edit there to change rules and format)
- OpenRouter LLM for subject/body generation and agent reasoning
- Real email sending via Gmail SMTP
- React dashboard, datasets, AI chat, and campaigns UI

## Quick start

### 1. MySQL

```sql
CREATE DATABASE email_agent_db;
```

### 2. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env         # Fill in keys

# Quick demo without MySQL: in .env set USE_SQLITE=true

uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
copy .env.example .env        # Windows — set VITE_API_URL to your FastAPI URL
npm run dev
```

| File | Purpose |
|------|---------|
| `frontend/.env` | `VITE_API_URL` — backend base URL (e.g. `http://localhost:8000`). Not committed to git. |

Restart `npm run dev` after changing `frontend/.env`.

Open [http://localhost:3000](http://localhost:3000)

### Vercel (two deployment options)

| Vercel project | Root Directory | Config file | What it deploys |
|----------------|----------------|-------------|-----------------|
| **A — Monorepo** | `.` (repo root) | `vercel.json` | Runs `cd frontend && npm run build`, serves `frontend/dist` |
| **B — Frontend only** | `frontend` | `frontend/vercel.json` | Vite build from package root; SPA rewrites |

Create **two Vercel projects** linked to the same Git repo if you want separate URLs (e.g. staging vs production), or one project using **A** for the UI.

**Backend (FastAPI):** deploy separately (Railway, Render, Fly.io, etc.). Set `VITE_API_URL` in the Vercel project **Environment Variables** to that API origin (no trailing slash).

### 4. Configure `.env`


| Variable             | Description                                                                                                                                                  |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `OPENROUTER_API_KEY` | From [openrouter.ai](https://openrouter.ai)                                                                                                                  |
| `OPENROUTER_MODEL`   | Use a model that supports **tool use** (e.g. `openai/gpt-4o-mini`). If chat returns 404 from OpenRouter, the model has no tool-capable route — change model. |
| `DB_URL`             | MySQL connection string                                                                                                                                      |
| `SMTP_`*             | Gmail: use an **App Password**, not your normal password (see below)                                                                                      |

### Turso (optional, when using SQLite mode)

If you want managed SQLite (Turso/libSQL) instead of local `email_agent.db`:

```env
USE_SQLITE=true
TURSO_DATABASE_URL=libsql://your-db-name.turso.io
TURSO_AUTH_TOKEN=your_turso_auth_token
```

Then restart the backend. Keep `DB_URL` for MySQL mode only.

### Gmail SMTP (fix “535 Username and Password not accepted”)

1. Turn on **2-Step Verification** on the Google account.
2. Open **Google Account → Security → App passwords** (or search “App passwords”).
3. Create an app password for **Mail** (e.g. device “Other” → name it “Email Agent”).
4. In `backend/.env` set `SMTP_USER` to the **full Gmail address** and `SMTP_PASSWORD` to the **16-character app password** (spaces optional).
5. Restart the backend after changing `.env`.

If you use a non-Gmail provider, use its SMTP settings instead.

### AI chat behavior

- **Context:** The last **15** stored Q/A pairs (configurable via `CHAT_HISTORY_MAX_TURNS` in `.env`) are passed into the agent as **`chat_history`**, so follow-ups remember things like the dataset you named.
- **Choice questions:** If your prompt is incomplete (no dataset, unclear send vs draft, etc.), the API returns **`clarification`** with clickable options in the UI—no slow agent run until you pick one.
- **Draft:** Prompts like “create a birthday campaign” create a **draft** only. If you do not name a dataset, the agent **lists datasets and asks which one** — it should not pick one for you.
- **Send:** Real SMTP sends happen only when you clearly ask to **send / deliver / dispatch** (or you use **Campaigns → Send**).
- After changing agent code, **restart the backend** so the updated instructions load (the agent is cached in memory).

## Sample flow

1. Upload `sample-data/startup_leads.csv` on the Datasets page.
2. In AI Chat, try: *"Use dataset 1 and send a promotional campaign about 50% discount"*
3. View the campaign on the Campaigns page and check send logs.

## Project structure

See `Ai email marketing agent plan.md` for full architecture and ER diagram.