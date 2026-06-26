"""
ML classifier service for resume categorisation.

Trains and compares SVM, Random Forest, KNN, and Naive Bayes classifiers
on the Kaggle resume dataset. Two classification approaches:

1. Category Classifier: Predicts which job category a resume belongs to
   (IT, Engineering, Finance, etc.) using TF-IDF features from resume text.

2. Quality Classifier: Predicts Highly Qualified / Qualified / Not Qualified
   based on extracted features (skills match, experience, education, etc.)

Both approaches are evaluated with precision, recall, F1, and accuracy.
"""
import os
import json
import pickle
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
from sklearn.preprocessing import LabelEncoder
import re
import time


# Path to store trained models and results
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "models")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")


def _clean_resume_text(text):
    """Clean resume text for TF-IDF processing."""
    if not isinstance(text, str):
        return ""
    # Remove URLs
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    # Remove special characters but keep spaces
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text.lower()


def load_dataset():
    """Load and prepare the Kaggle resume dataset."""
    csv_path = os.path.join(DATA_DIR, "UpdatedResumeDataSet.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Dataset not found at {csv_path}. "
            "Download from https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset "
            "and place UpdatedResumeDataSet.csv in backend/data/"
        )

    df = pd.read_csv(csv_path)
    df["cleaned"] = df["Resume_str"].apply(_clean_resume_text)

    # Remove empty resumes
    df = df[df["cleaned"].str.len() > 50].reset_index(drop=True)

    return df


def train_all_classifiers(test_size=0.2, random_state=42):
    """Train all four classifiers and return comparison metrics.

    Returns:
        dict with model results, confusion matrices, and evaluation metrics
    """
    os.makedirs(MODEL_DIR, exist_ok=True)

    # Load dataset
    df = load_dataset()

    # Encode labels
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df["Category"])
    categories = label_encoder.classes_.tolist()

    # TF-IDF vectorisation
    tfidf = TfidfVectorizer(max_features=5000, stop_words="english", ngram_range=(1, 2))
    X = tfidf.fit_transform(df["cleaned"])

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # Define classifiers
    classifiers = {
        "SVM": SVC(kernel="linear", probability=True, random_state=random_state),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=random_state),
        "KNN": KNeighborsClassifier(n_neighbors=5),
        "Naive Bayes": MultinomialNB(),
    }

    results = {}

    for name, clf in classifiers.items():
        start_time = time.time()

        # Train
        clf.fit(X_train, y_train)
        train_time = time.time() - start_time

        # Predict
        start_time = time.time()
        y_pred = clf.predict(X_test)
        predict_time = time.time() - start_time

        # Metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)

        # Per-class report
        report = classification_report(y_test, y_pred, target_names=categories, output_dict=True, zero_division=0)

        # Cross-validation score (5-fold)
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

        # Save the trained model
        model_path = os.path.join(MODEL_DIR, f"{name.lower().replace(' ', '_')}.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(clf, f)

    # Save TF-IDF vectoriser and label encoder
    with open(os.path.join(MODEL_DIR, "tfidf.pkl"), "wb") as f:
        pickle.dump(tfidf, f)
    with open(os.path.join(MODEL_DIR, "label_encoder.pkl"), "wb") as f:
        pickle.dump(label_encoder, f)

    # Save results
    with open(os.path.join(MODEL_DIR, "evaluation_results.json"), "w") as f:
        json.dump({
            "results": results,
            "categories": categories,
            "dataset_size": len(df),
            "train_size": X_train.shape[0],
            "test_size": X_test.shape[0],
            "feature_count": X.shape[1],
        }, f, indent=2)

    return {
        "results": results,
        "categories": categories,
        "dataset_size": len(df),
        "train_size": X_train.shape[0],
        "test_size": X_test.shape[0],
    }


def classify_resume(resume_text):
    """Classify a single resume using all trained models.

    Returns predicted category from each classifier.
    """
    # Load models
    try:
        with open(os.path.join(MODEL_DIR, "tfidf.pkl"), "rb") as f:
            tfidf = pickle.load(f)
        with open(os.path.join(MODEL_DIR, "label_encoder.pkl"), "rb") as f:
            label_encoder = pickle.load(f)
    except FileNotFoundError:
        raise Exception("Models not trained yet. Run training first.")

    cleaned = _clean_resume_text(resume_text)
    X = tfidf.transform([cleaned])

    predictions = {}
    model_files = {
        "SVM": "svm.pkl",
        "Random Forest": "random_forest.pkl",
        "KNN": "knn.pkl",
        "Naive Bayes": "naive_bayes.pkl",
    }

    for name, filename in model_files.items():
        model_path = os.path.join(MODEL_DIR, filename)
        if not os.path.exists(model_path):
            continue

        with open(model_path, "rb") as f:
            clf = pickle.load(f)

        pred_idx = clf.predict(X)[0]
        category = label_encoder.inverse_transform([pred_idx])[0]

        # Get probability if available
        if hasattr(clf, "predict_proba"):
            proba = clf.predict_proba(X)[0]
            confidence = round(float(max(proba)) * 100, 1)
        else:
            confidence = None

        predictions[name] = {
            "category": category,
            "confidence": confidence,
        }

    return predictions


def get_evaluation_results():
    """Load saved evaluation results from both datasets."""
    results = {}

    # Dataset 1: Resume text classification
    path1 = os.path.join(MODEL_DIR, "evaluation_results.json")
    if os.path.exists(path1):
        with open(path1, "r") as f:
            results["dataset1"] = json.load(f)

    # Dataset 2: Structured features classification
    path2 = os.path.join(MODEL_DIR, "evaluation_results_structured.json")
    if os.path.exists(path2):
        with open(path2, "r") as f:
            results["dataset2"] = json.load(f)

    return results if results else None


def train_structured_classifiers(test_size=0.2, random_state=42):
    """Train classifiers on the structured candidate dataset.

    Uses skills, qualification, and experience_level as features
    to predict job_role. This is feature-based classification
    as opposed to the text-based TF-IDF approach in Dataset 1.
    """
    os.makedirs(MODEL_DIR, exist_ok=True)

    csv_path = os.path.join(DATA_DIR, "candidate_job_role_dataset.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Dataset not found at {csv_path}. "
            "Place candidate_job_role_dataset.csv in backend/data/"
        )

    df = pd.read_csv(csv_path)

    # Combine skills + qualification + experience into a single text feature
    # This lets us use TF-IDF on the combined text for consistent comparison
    df["combined_features"] = (
        df["skills"].fillna("") + " " +
        df["qualification"].fillna("") + " " +
        df["experience_level"].fillna("")
    )

    # Clean
    df["combined_features"] = df["combined_features"].apply(_clean_resume_text)
    df = df[df["combined_features"].str.len() > 5].reset_index(drop=True)

    # Encode labels
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df["job_role"])
    categories = label_encoder.classes_.tolist()

    # TF-IDF on combined features
    tfidf = TfidfVectorizer(max_features=3000, stop_words="english", ngram_range=(1, 2))
    X = tfidf.fit_transform(df["combined_features"])

    # Split
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

    for name, clf in classifiers.items():
        start_time = time.time()
        clf.fit(X_train, y_train)
        train_time = time.time() - start_time

        start_time = time.time()
        y_pred = clf.predict(X_test)
        predict_time = time.time() - start_time

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

        # Save model
        model_path = os.path.join(MODEL_DIR, f"structured_{name.lower().replace(' ', '_')}.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(clf, f)

    # Save vectoriser and encoder
    with open(os.path.join(MODEL_DIR, "structured_tfidf.pkl"), "wb") as f:
        pickle.dump(tfidf, f)
    with open(os.path.join(MODEL_DIR, "structured_label_encoder.pkl"), "wb") as f:
        pickle.dump(label_encoder, f)

    # Save results
    with open(os.path.join(MODEL_DIR, "evaluation_results_structured.json"), "w") as f:
        json.dump({
            "results": results,
            "categories": categories,
            "dataset_size": len(df),
            "train_size": X_train.shape[0],
            "test_size": X_test.shape[0],
            "feature_count": X.shape[1],
            "dataset_name": "Candidate Job Role Dataset",
            "approach": "Structured Features (Skills + Qualification + Experience)",
        }, f, indent=2)

    return {
        "results": results,
        "categories": categories,
        "dataset_size": len(df),
        "train_size": X_train.shape[0],
        "test_size": X_test.shape[0],
    }
