<!-- omit in toc -->

# CSE573 LinkedIn Assistant

An explainable job-search copilot that ingests a resume, stages curated roles from the provided Excel dataset, scores every requirement with Rasch/Guttman math, and chats about apply/network/upskill tactics through a modern multi-step UI.

## Demo


https://github.com/user-attachments/assets/27120385-6443-4224-a12c-2f0f48a4030f



## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Environment Variables](#environment-variables)
- [Running the Full Stack](#running-the-full-stack)
- [Testing the Workflow](#testing-the-workflow)
- [License](#license)
- [Contributors](#contributors)

## Features

- **Resume parsing** – Accepts PDF/DOC/DOCX/TXT, extracts education + experience + skills, and estimates the candidate’s θ (ability).
- **Dataset search** – Loads `linkedin_job_posts_insights.xlsx` via Pandas and supports keyword/fuzzy matching across ~31K roles.
- **Rasch/Guttman scoring** – Compares candidate θ to each requirement’s difficulty b, exposing per-item probabilities so matches are transparent.
- **Conversational agent** – Chatbot uses the parsed profile + dataset context to answer job, resume, networking, or upskilling questions with intent-aware sections.
- **Next.js workflow UI** – Four steps (resume, dataset, scoring, chat) with pastel glassmorphism, animated hero text, and consistent navigation.

## Architecture

```
                ┌─────────────────────┐
                │ Next.js Frontend    │
                │ (steps + chatbot)   │
                └────────┬────────────┘
                         │ proxy (/api/backend/…)
┌────────────────────────┴────────────────────────┐
│                FastAPI Backend                  │
│  parsers ─ resume/job                           │
│  matching ─ Rasch scorer                        │
│  retrieval ─ TF-IDF + embeddings                │
│  chatbot ─ templated agent + intents            │
│  dataset ─ linkedin_job_posts_insights.xlsx     │
└────────────────────────┬────────────────────────┘
                         │
                In-memory profile/jobs
```

## Tech Stack

- **Backend:** Python 3.12, FastAPI, Pydantic, Pandas, Scikit-learn, RapidFuzz
- **Frontend:** Next.js 15 (App Router), React 19 RC, Tailwind CSS
- **Matching:** Custom Rasch/Guttman implementation + TF-IDF baseline
- **Chatbot:** Template/intent driven agent referencing the parsed profile & dataset jobs

## Project Structure

```
.
├── backend
│   ├── app.py                # FastAPI entrypoint + endpoints
│   ├── models.py             # Pydantic schemas / DTOs
│   ├── parsers/              # resume_parser.py, job_parser.py
│   ├── matching/             # rasch.py, matcher.py
│   ├── retrieval/            # tfidf.py, embeddings.py
│   ├── chatbot/              # agent.py (chat logic)
│   ├── data/                 # loader for linkedin_job_posts_insights.xlsx
│   └── graph/, storage/, agents/ (scaffolds for future work)
├── frontend
│   ├── src/
│   │   ├── app/              # Next.js pages (home + steps)
│   │   ├── components/       # GlassCard, StepNav, etc.
│   │   └── lib/              # API helper + shared types
│   ├── public/               # Static assets
│   └── env.example           # Frontend env vars
├── linkedin_job_posts_insights.xlsx
├── requirements.txt          # Backend Python deps
├── README.md
└── LICENSE
```

## Prerequisites

- Python **3.12.x**
- Node.js **>=18**
- npm **>=9**

## Backend Setup

```bash
# From project root
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

# Run FastAPI with auto-reload
uvicorn backend.app:app --reload
# API: http://127.0.0.1:8000  |  Docs: /docs
```

## Frontend Setup

```bash
cd frontend
npm install

# Start dev server (http://localhost:3000 or 3001)
npm run dev
```

## Environment Variables

Frontend proxies to the backend via `/api/backend/...`. Copy the example file:

```
cd frontend
cp env.example .env.local
```

`env.example` exposes two knobs:

| Variable                   | Description                                  | Default                 |
| -------------------------- | -------------------------------------------- | ----------------------- |
| `NEXT_PUBLIC_API_BASE_URL` | Browser calls (should remain `/api/backend`) | `/api/backend`          |
| `BACKEND_URL`              | Where the proxy forwards requests            | `http://127.0.0.1:8000` |

The backend needs no env vars; it loads the Excel dataset from the repo root on startup and stores everything in memory.

## Running the Full Stack

1. **Backend**
   ```bash
   source .venv/bin/activate
   uvicorn backend.app:app --reload
   ```
2. **Frontend**
   ```bash
   cd frontend
   npm run dev
   ```
3. Visit `http://localhost:3000` (or the port Next.js reports) and follow the step-by-step flow:
   - Step 1: Upload a resume (PDF/TXT/etc.).
   - Step 2: Query the curated dataset (`data scientist remote` is a good starter).
   - Step 3: Refresh Rasch suggestions to see per-item probabilities.
   - Step 4: Chat with the assistant for job/resume/network/upskill advice.

## Testing the Workflow

1. Create a quick sample resume (TXT works) and upload in Step 1.
2. Search for roles (`data scientist`, `product manager seattle`, etc.) in Step 2.
3. Hit “Refresh suggestions” in Step 3 to populate Rasch matches.
4. In Step 4, try intent-specific prompts:
   - “Suggest remote data engineer roles with high fit.”
   - “Rewrite my AWS migration bullet.”
   - “Draft a LinkedIn message to a PayPal analytics lead.”
   - “What should I upskill to reach senior analyst level?”

## Evaluation Results

See detailed metrics, method comparison tables, system performance, and explainability analysis in [evaluation.md](./evaluation.md).

---

## Dataset

- Kaggle LinkedIn Job Posts Insights : [linkedin_job_posts_insights](./linkedin_job_posts_insights.xlsx).

## License

This project is licensed under the [MIT License](./LICENSE).

