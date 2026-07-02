# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Smart Resume Matcher is a two-tier web application: a React SPA frontend and a Flask REST API backend backed by MongoDB. It parses CVs (PDF/DOCX), extracts skills via NLP, and scores candidates against job postings using a weighted algorithm plus optional ML classifiers.

## Commands

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate                        # Windows
pip install -r requirements.txt
python -m spacy download en_core_web_sm      # Required — NOT in requirements.txt
python run.py                                # Starts at http://localhost:5000
```

Seed data (optional, one-time):
```bash
python seed_jobs.py
python seed_skills_from_dataset.py
```

Train ML classifiers (one-off HTTP call, takes 30-60s):
```
POST http://localhost:5000/api/evaluation/train
```

### Frontend

```bash
cd frontend
npm install
npm run dev      # Dev server at http://localhost:5173
npm run build
npm run lint
```

### Tests

```bash
cd backend
python -m pytest tests/test_api.py -v
```

Tests run against the **real local MongoDB** (not mocked). MongoDB must be running. The cleanup fixture targets documents where `company == "Test Corp"`.

## Architecture

### Backend (`backend/app/`)

**App factory** (`app/__init__.py`): `create_app()` bootstraps Flask, CORS, MongoDB connection, skill taxonomy seeding, and blueprint registration. A single module-level `db` variable is imported directly by all route modules (`from app import db`) — there is no dependency injection.

**Blueprints** (`app/routes/`): One file per domain — `health`, `jobs`, `resumes`, `evaluation`, `taxonomy`, `docs`.

**Services** (`app/services/`): The core logic lives here.

| File | Responsibility |
|---|---|
| `parser.py` | Raw text extraction from PDF (PyMuPDF) and DOCX (python-docx) |
| `section_parser.py` | Regex-based splitting of raw text into sections (contact, summary, skills, experience, education, projects) |
| `nlp_extractor.py` | spaCy NER + taxonomy skill matching + BERT embedding generation |
| `skill_taxonomy.py` | In-memory cache of MongoDB `skill_taxonomy` collection; fuzzy alias lookup via `difflib` at 0.80 threshold |
| `matcher.py` | Scoring engine: skills 40%, experience 30%, education 10%, projects 20%, +5pt semantic BERT bonus |
| `embedding.py` | Lazy-loads `all-MiniLM-L6-v2` sentence-transformer on first call |
| `classifier.py` | Trains/runs SVM, Random Forest, KNN, Naive Bayes on TF-IDF features; models pickled to `backend/data/models/` |
| `evaluation.py` | Orchestrates classifier training from CSV datasets in `backend/data/` |

**Resume processing flow**: upload → `parser.py` → `section_parser.py` → `nlp_extractor.py` → MongoDB (`status`: `uploaded` → `parsing` → `parsed` or `failed`).

**Matching flow**: `POST /api/jobs/:id/match` → `matcher.py` scores all `parsed` resumes → results in `match_results` collection → categorised as `highly_qualified` (≥75), `qualified` (≥50), or `not_qualified` (<50).

**Important side effect**: `PUT /api/jobs/:id` deletes all associated resumes (disk + DB) and match results. HR must re-upload CVs after any job edit.

### Frontend (`frontend/src/`)

- Single `services/api.js` with named exports for every endpoint — all backend calls go through here.
- Six pages: Dashboard, Jobs, Resumes, Results, Evaluation, Taxonomy.
- React Router v7 with sidebar `NavLink` navigation. No global state management — local React state only.

### Database (MongoDB)

Database: `smart_resume_matcher`  
Collections: `jobs`, `resumes`, `match_results`, `skill_taxonomy`, `soft_skills`

### ML Data

CSV training datasets are in `backend/data/`:
- `AI_Resume_Screening.csv` — 1000 resumes, 4 IT roles
- `resume_data.csv` — 9544 resumes, 28 job positions

## Key Notes

- **spaCy model**: `en_core_web_sm` must be downloaded separately; it is not in `requirements.txt`.
- **Legacy `.doc` support**: Requires LibreOffice (`soffice`) in PATH; falls back to binary ASCII extraction without it.
- **Uploaded files**: Stored as `{uuid4().hex}_{original_filename}` under `backend/uploads/`.
- **Stale file**: `backend/app/services/section_parser - Copy.py` is a backup and not imported anywhere.
- **No authentication**: All API endpoints are publicly accessible.
- **API reference**: `backend/API_DOCS.md` documents all endpoints.
