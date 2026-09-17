# Smart Resume Matcher

> Automated CV sorting for hiring teams — paste in a job description, drop in a stack of CVs, get back a ranked shortlist with match explanations.

<!--
  Fill in when available. If not deployed yet, replace the demo line with:
  🚧 Live demo coming soon. Screenshots below.
-->
🔗 **Live demo:** _coming soon_ · 🎓 **Dissertation:** MSc Data Science, UWE Bristol — supervised by Ahsan Kazmi · 🖼️ Screenshots below

<!--
  Add one wide GIF (~15s) here showing: upload JD → upload CVs → ranked list appears.
  If you can't do a GIF, use two stills: (1) upload screen, (2) ranked results view.
  Commit as docs/hero.gif or docs/screenshot-1.png etc.
-->

<!-- ![Smart Resume Matcher — ranked shortlist view](docs/hero.gif) -->

---

## What it does

Recruiters at small teams spend hours skimming CVs against a JD. Smart Resume Matcher automates the first pass: it parses PDFs and Word docs, extracts skills and experience, embeds both the JD and each CV in a shared semantic space, then returns a ranked shortlist with a match score and the top overlapping skills so the human reviewer knows *why* each CV made the cut.

## Why this exists

Keyword-matching Applicant Tracking Systems are famously blunt — they miss strong candidates whose CVs phrase things differently from the JD, and they surface weak ones who happened to keyword-stuff. This project was built as my MSc Data Science dissertation at UWE Bristol to test whether a small, transparent NLP pipeline could do meaningfully better than keyword matching on the same data, while staying explainable enough for a human recruiter to trust the ranking.

## How it works

```
   JD text            CV files (.pdf, .docx)
      │                       │
      ▼                       ▼
  ┌─────────┐          ┌──────────────┐
  │ Cleanup │          │ Parse & OCR  │  ← PyMuPDF, python-docx
  └────┬────┘          └──────┬───────┘
       │                      │
       ▼                      ▼
   ┌───────────────────────────────┐
   │  NLP pipeline (spaCy + BERT)  │  ← tokenise, entity extract, embed
   └───────────────┬───────────────┘
                   │
                   ▼
   ┌───────────────────────────────┐
   │  Match & classify             │  ← SVM · Random Forest · KNN · Naive Bayes
   │  (best model selected per     │     compared on the dissertation dataset;
   │  benchmark; see results)      │     see the dissertation for details
   └───────────────┬───────────────┘
                   │
                   ▼
        Ranked shortlist + score + top matched skills → React (Vite) UI
                                                        ← results stored in MongoDB
```

The backend is a Flask API; MongoDB stores job postings, uploaded CVs, and match results. The frontend is a small React + Vite app for uploading JDs and CVs and viewing the ranked output.

## Results

<!--
  Replace the placeholders below with the actual numbers from your dissertation.
  Recruiters skim this — one line per metric, no essays.
-->
<!--

On the dissertation benchmark dataset:

| Model                | Accuracy | Precision | Recall | F1 |
|----------------------|:--------:|:---------:|:------:|:--:|
| Naive Bayes          |   `--`   |   `--`    |  `--`  |`--`|
| KNN                  |   `--`   |   `--`    |  `--`  |`--`|
| SVM                  |   `--`   |   `--`    |  `--`  |`--`|
| Random Forest        |   `--`   |   `--`    |  `--`  |`--`|
| **BERT + best model** |  `--`    |   `--`    |  `--`  |`--`|

Full methodology, ablations, and error analysis in the dissertation write-up.
-->

## Tech stack

**Backend** — Python · Flask · MongoDB
**NLP / ML** — spaCy · BERT (Hugging Face) · scikit-learn (SVM, Random Forest, KNN, Naive Bayes)
**Document parsing** — PyMuPDF · python-docx
**Frontend** — React · Vite

## Running it locally

Requirements: Python 3.10+, Node 18+, MongoDB running locally on default port.

Clone the repo:

```bash
git clone https://github.com/Mokaddis-ALIF/smart-resume-matcher.git
cd smart-resume-matcher
```

**Backend** (Flask API — port 5000):

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```

**Frontend** (Vite dev server — port 5173):

```bash
cd frontend
npm install
npm run dev
```

Seed sample jobs into MongoDB:

```bash
mongoimport --db smart_resume_matcher --collection jobs --file smart_resume_matcher.jobs.json
```

## Repository layout

```
smart-resume-matcher/
├── backend/                    # Flask API, NLP pipeline, model training
├── frontend/                   # React + Vite UI
├── smart_resume_matcher.jobs.json   # Sample job postings for local seed
└── docs/                       # Screenshots, GIF, architecture diagram
```

## Dissertation

Built as my MSc Data Science dissertation at the **University of the West of England (UWE Bristol)**, supervised by **Ahsan Kazmi**. Awarded a Merit. The dissertation covers the dataset, the four-model comparison, the BERT integration, and a discussion of failure modes (short CVs, non-standard JDs, multilingual candidates).

## Roadmap

- Deploy a public demo (currently local-only)
- Add feedback loop: recruiter marks a match right/wrong, model retrains on the delta
- Multilingual CV support (spaCy pipelines for `xx`)
- Explanations at the sentence level, not just the skill level

## Licence

MIT — see [`LICENSE`](LICENSE).

---

Built by **Mokaddis Borhan Alif** · Bristol, UK · [mokaddis.alif@gmail.com](mailto:mokaddis.alif@gmail.com) · [GitHub](https://github.com/Mokaddis-ALIF)
