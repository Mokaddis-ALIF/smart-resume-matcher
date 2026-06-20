# Smart Resume Matching Tool

MSc Data Science Dissertation Project — Automated CV sorting system using NLP and Machine Learning.

## Tech Stack

- **Backend:** Python (Flask), MongoDB (PyMongo)
- **NLP:** spaCy, Hugging Face Transformers (BERT)
- **ML:** scikit-learn (SVM, Random Forest, KNN, Naive Bayes)
- **Document Parsing:** PyMuPDF, python-docx
- **Frontend:** React (Vite)

## Project Structure

```
smart-resume-matcher/
├── backend/
│   ├── app/
│   │   ├── routes/        # API endpoint definitions
│   │   ├── services/      # Business logic (parsing, NLP, matching)
│   │   ├── models/        # MongoDB document schemas
│   │   ├── utils/         # Helper functions
│   │   ├── config.py      # App configuration
│   │   └── __init__.py    # Flask app factory
│   ├── uploads/           # Uploaded CV files
│   ├── tests/             # Unit & integration tests
│   ├── run.py             # App entry point
│   ├── requirements.txt   # Python dependencies
│   └── .env               # Environment variables
├── frontend/
│   └── src/
│       ├── components/    # Reusable UI components
│       ├── pages/         # Page-level components
│       ├── services/      # API call functions
│       └── assets/        # Static files (images, icons)
├── .gitignore
└── README.md
```

## Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
