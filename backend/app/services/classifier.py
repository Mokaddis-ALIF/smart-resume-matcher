"""
ML classifier service for resume categorisation.

Trains and compares SVM, Random Forest, KNN, and Naive Bayes classifiers
across two datasets:

Dataset 1 — AI_Resume_Screening.csv (1000 resumes, 4 job roles)
    Features: Skills + Education + Experience + Certifications

Dataset 2 — resume_data.csv (9544 resumes, 28 job positions)
    Features: skills + degree_names + major_field_of_studies + career_objective

Both use TF-IDF vectorisation. Metrics collected: accuracy, precision, recall,
F1, 5-fold CV mean/std, per-class report, confusion matrix, train/predict time.
"""
import os
import json
import pickle
import time
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix,
)
from sklearn.preprocessing import LabelEncoder


MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "models")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")


def _clean_resume_text(text):
    """Clean text for TF-IDF processing (strips URLs, punctuation, extra whitespace, lowercases)."""
    if not isinstance(text, str):
        return ""
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.lower()


def _evaluate_classifiers(X, y, categories, test_size=0.2, random_state=42):
    """Shared training loop — fits each classifier, collects all metrics.

    Returns:
        (results dict, fitted classifiers dict, train_size, test_size)
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    classifiers = {
        "SVM": SVC(kernel="linear", probability=True, random_state=random_state),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=random_state),
        "KNN": KNeighborsClassifier(n_neighbors=5),
        "Naive Bayes": MultinomialNB(),
    }

    results = {}
    fitted = {}

    for name, clf in classifiers.items():
        t0 = time.time()
        clf.fit(X_train, y_train)
        train_time = time.time() - t0

        t0 = time.time()
        y_pred = clf.predict(X_test)
        predict_time = time.time() - t0

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
        cm = confusion_matrix(y_test, y_pred)
        report = classification_report(y_test, y_pred, target_names=categories, output_dict=True, zero_division=0)
        cv_scores = cross_val_score(clf, X, y, cv=5, scoring="accuracy")

        results[name] = {
            "accuracy": round(accuracy * 100, 2),
            "precision": round(precision * 100, 2),
            "recall": round(recall * 100, 2),
            "f1_score": round(f1 * 100, 2),
            "train_time_seconds": round(train_time, 3),
            "predict_time_seconds": round(predict_time, 3),
            "cv_mean_accuracy": round(cv_scores.mean() * 100, 2),
            "cv_std": round(cv_scores.std() * 100, 2),
            "confusion_matrix": cm.tolist(),
            "per_class_report": {
                cat: {
                    "precision": round(report[cat]["precision"] * 100, 2),
                    "recall": round(report[cat]["recall"] * 100, 2),
                    "f1_score": round(report[cat]["f1-score"] * 100, 2),
                    "support": report[cat]["support"],
                }
                for cat in categories if cat in report
            },
        }
        fitted[name] = clf

    return results, fitted, X_train.shape[0], X_test.shape[0]


def _save_models(fitted, tfidf, label_encoder, prefix):
    """Persist trained models, vectoriser, and label encoder with a common prefix."""
    for name, clf in fitted.items():
        path = os.path.join(MODEL_DIR, f"{prefix}{name.lower().replace(' ', '_')}.pkl")
        with open(path, "wb") as f:
            pickle.dump(clf, f)
    with open(os.path.join(MODEL_DIR, f"{prefix}tfidf.pkl"), "wb") as f:
        pickle.dump(tfidf, f)
    with open(os.path.join(MODEL_DIR, f"{prefix}label_encoder.pkl"), "wb") as f:
        pickle.dump(label_encoder, f)


# ---------- Dataset 1: AI Resume Screening ----------

def train_ai_screening_classifiers(test_size=0.2, random_state=42):
    """Train classifiers on the AI Resume Screening dataset (1000 resumes, 4 job roles)."""
    os.makedirs(MODEL_DIR, exist_ok=True)

    csv_path = os.path.join(DATA_DIR, "AI_Resume_Screening.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}")

    df = pd.read_csv(csv_path)

    df["combined_features"] = (
        df["Skills"].fillna("") + " " +
        df["Education"].fillna("") + " " +
        df["Experience (Years)"].astype(str).fillna("") + " " +
        df["Certifications"].fillna("")
    ).apply(_clean_resume_text)
    df = df[df["combined_features"].str.len() > 5].reset_index(drop=True)

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df["Job Role"])
    categories = label_encoder.classes_.tolist()

    tfidf = TfidfVectorizer(max_features=3000, stop_words="english", ngram_range=(1, 2))
    X = tfidf.fit_transform(df["combined_features"])

    results, fitted, train_n, test_n = _evaluate_classifiers(X, y, categories, test_size, random_state)

    _save_models(fitted, tfidf, label_encoder, prefix="ai_screening_")

    output = {
        "results": results,
        "categories": categories,
        "dataset_size": len(df),
        "train_size": train_n,
        "test_size": test_n,
        "feature_count": X.shape[1],
        "dataset_name": "AI Resume Screening Dataset",
        "approach": "Structured Features (Skills + Education + Experience + Certifications)",
    }

    with open(os.path.join(MODEL_DIR, "evaluation_results_ai_screening.json"), "w") as f:
        json.dump(output, f, indent=2)

    return output


# ---------- Dataset 2: Resume Data (Job Position) ----------

def train_structured_classifiers(test_size=0.2, random_state=42):
    """Train classifiers on resume_data.csv (9544 resumes, 28 job positions).

    Note: the target column ships with a BOM prefix (\ufeffjob_position_name)
    in the raw CSV — normalised here before use.
    """
    os.makedirs(MODEL_DIR, exist_ok=True)

    csv_path = os.path.join(DATA_DIR, "resume_data.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}")

    df = pd.read_csv(csv_path, low_memory=False)

    # Normalise BOM on the target column if present
    target_col = "job_position_name"
    if "\ufeffjob_position_name" in df.columns:
        df = df.rename(columns={"\ufeffjob_position_name": target_col})

    df["combined_features"] = (
        df["skills"].fillna("") + " " +
        df["degree_names"].fillna("") + " " +
        df["major_field_of_studies"].fillna("") + " " +
        df["career_objective"].fillna("")
    ).apply(_clean_resume_text)

    df = df.dropna(subset=[target_col]).reset_index(drop=True)
    df = df[df["combined_features"].str.len() > 5].reset_index(drop=True)

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df[target_col])
    categories = label_encoder.classes_.tolist()

    tfidf = TfidfVectorizer(max_features=5000, stop_words="english", ngram_range=(1, 2))
    X = tfidf.fit_transform(df["combined_features"])

    results, fitted, train_n, test_n = _evaluate_classifiers(X, y, categories, test_size, random_state)

    _save_models(fitted, tfidf, label_encoder, prefix="resume_data_")

    output = {
        "results": results,
        "categories": categories,
        "dataset_size": len(df),
        "train_size": train_n,
        "test_size": test_n,
        "feature_count": X.shape[1],
        "dataset_name": "Resume Data (Job Position) Dataset",
        "approach": "Structured Features (Skills + Degree + Field + Career Objective)",
    }

    with open(os.path.join(MODEL_DIR, "evaluation_results_resume_data.json"), "w") as f:
        json.dump(output, f, indent=2)

    return output


# ---------- Results loading & single-resume classification ----------

def get_evaluation_results():
    """Load saved evaluation results from both datasets into a single dict.

    Returns {"dataset1": {...}, "dataset2": {...}} or None if neither exists.
    """
    results = {}

    p1 = os.path.join(MODEL_DIR, "evaluation_results_ai_screening.json")
    if os.path.exists(p1):
        with open(p1, "r") as f:
            results["dataset1"] = json.load(f)

    p2 = os.path.join(MODEL_DIR, "evaluation_results_resume_data.json")
    if os.path.exists(p2):
        with open(p2, "r") as f:
            results["dataset2"] = json.load(f)

    return results if results else None


def classify_resume(resume_text, dataset=1):
    """Classify a resume text using all four trained models from the chosen dataset.

    Args:
        resume_text: Raw resume text.
        dataset: 1 = AI Resume Screening (4 broad IT roles, default),
                 2 = resume_data.csv (28 specific job positions).
    """
    prefix = "ai_screening_" if dataset == 1 else "resume_data_"

    try:
        with open(os.path.join(MODEL_DIR, f"{prefix}tfidf.pkl"), "rb") as f:
            tfidf = pickle.load(f)
        with open(os.path.join(MODEL_DIR, f"{prefix}label_encoder.pkl"), "rb") as f:
            label_encoder = pickle.load(f)
    except FileNotFoundError:
        raise Exception(f"Dataset {dataset} models not trained yet. Run training first.")

    cleaned = _clean_resume_text(resume_text)
    X = tfidf.transform([cleaned])

    predictions = {}
    for name in ["SVM", "Random Forest", "KNN", "Naive Bayes"]:
        filename = f"{prefix}{name.lower().replace(' ', '_')}.pkl"
        model_path = os.path.join(MODEL_DIR, filename)
        if not os.path.exists(model_path):
            continue

        with open(model_path, "rb") as f:
            clf = pickle.load(f)

        pred_idx = clf.predict(X)[0]
        category = label_encoder.inverse_transform([pred_idx])[0]

        if hasattr(clf, "predict_proba"):
            proba = clf.predict_proba(X)[0]
            confidence = round(float(max(proba)) * 100, 1)
        else:
            confidence = None

        predictions[name] = {"category": category, "confidence": confidence}

    return predictions
