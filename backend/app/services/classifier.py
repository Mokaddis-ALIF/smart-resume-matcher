"""
ML classifier service — rebuilt for dissertation evaluation.

Dataset 1 — AI_Resume_Screening.csv (1,000 rows, 4 job roles)
    Features: Skills + Education + Experience (Years) + Certifications -> TF-IDF (3000 features)

Dataset 2 — resume_dataset_2.csv (815 rows, 5 job roles)
    Feature: cleaned Resume_Text only -> TF-IDF (5000 features)
    Run twice: raw and with role strings removed to quantify label leakage.

TF-IDF is fit on the training split only (no test-data leakage in holdout metrics).
5-fold CV uses a full Pipeline so the vectoriser is re-fit within each fold.

Note: cv_mean_accuracy stores 5-fold cross-validated MACRO-F1 (not accuracy).
"""

import os
import json
import pickle
import time
import re
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
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
DATA_DIR  = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
PLOT_DIR  = os.path.join(MODEL_DIR, "plots")

D1_CSV = os.path.join(DATA_DIR, "AI_Resume_Screening.csv")
D2_CSV = os.path.join(DATA_DIR, "resume_dataset_2.csv")

D2_ROLE_STRINGS = [
    "Software Engineer", "HR Executive", "Data Scientist",
    "Marketing Manager", "Financial Analyst",
]

_HEADER_RE = re.compile(
    r"^(name|email|phone|mobile|contact|linkedin|address)[:\s].*$",
    re.IGNORECASE | re.MULTILINE,
)

_MODEL_KEYS = ["SVM", "Random Forest", "KNN", "Naive Bayes"]


def _build_clf(name):
    return {
        "SVM":           SVC(kernel="linear", probability=True, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        "KNN":           KNeighborsClassifier(n_neighbors=5),
        "Naive Bayes":   MultinomialNB(),
    }[name]


def _clean(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.lower()


def _clean_d2(text, remove_roles=False):
    if not isinstance(text, str):
        return ""
    text = _HEADER_RE.sub("", text)
    if remove_roles:
        for role in D2_ROLE_STRINGS:
            text = re.sub(re.escape(role), " ", text, flags=re.IGNORECASE)
    return _clean(text)


def _run_pipeline(texts, y, categories, max_features):
    """
    80/20 stratified split (TF-IDF fit on train only) + 5-fold CV via Pipeline.
    Returns (results dict, fitted clfs dict, fitted tfidf, train_n, test_n).
    """
    texts = list(texts)
    X_tr_raw, X_te_raw, y_tr, y_te = train_test_split(
        texts, y, test_size=0.2, random_state=42, stratify=y
    )

    tfidf = TfidfVectorizer(max_features=max_features, ngram_range=(1, 2), stop_words="english")
    X_tr = tfidf.fit_transform(X_tr_raw)
    X_te = tfidf.transform(X_te_raw)

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    results = {}
    fitted = {}

    for name in _MODEL_KEYS:
        clf = _build_clf(name)

        t0 = time.time()
        clf.fit(X_tr, y_tr)
        train_t = time.time() - t0

        t0 = time.time()
        y_pred = clf.predict(X_te)
        pred_t = time.time() - t0

        acc  = accuracy_score(y_te, y_pred)
        w_p  = precision_score(y_te, y_pred, average="weighted", zero_division=0)
        w_r  = recall_score   (y_te, y_pred, average="weighted", zero_division=0)
        w_f1 = f1_score       (y_te, y_pred, average="weighted", zero_division=0)
        m_p  = precision_score(y_te, y_pred, average="macro",    zero_division=0)
        m_r  = recall_score   (y_te, y_pred, average="macro",    zero_division=0)
        m_f1 = f1_score       (y_te, y_pred, average="macro",    zero_division=0)
        cm   = confusion_matrix(y_te, y_pred)
        rpt  = classification_report(y_te, y_pred, target_names=categories,
                                     output_dict=True, zero_division=0)

        # CV uses a fresh Pipeline so TF-IDF is re-fit on each training fold
        pipe = Pipeline([
            ("tfidf", TfidfVectorizer(max_features=max_features, ngram_range=(1, 2),
                                      stop_words="english")),
            ("clf",   _build_clf(name)),
        ])
        cv_raw = cross_val_score(pipe, texts, y, cv=skf, scoring="f1_macro", n_jobs=1)

        results[name] = {
            "accuracy":              round(acc  * 100, 2),
            "f1_score":              round(w_f1 * 100, 2),   # weighted — used by frontend bars
            "macro_f1":              round(m_f1 * 100, 2),
            "precision":             round(w_p  * 100, 2),   # weighted
            "recall":                round(w_r  * 100, 2),   # weighted
            "macro_precision":       round(m_p  * 100, 2),
            "macro_recall":          round(m_r  * 100, 2),
            "cv_mean_accuracy":      round(cv_raw.mean() * 100, 2),  # 5-fold CV macro-F1
            "cv_std":                round(cv_raw.std()  * 100, 2),
            "cv_scores":             [round(s * 100, 2) for s in cv_raw.tolist()],
            "train_time_seconds":    round(train_t, 3),
            "predict_time_seconds":  round(pred_t,  4),
            "confusion_matrix":      cm.tolist(),
            "per_class_report": {
                cat: {
                    "precision": round(rpt[cat]["precision"] * 100, 2),
                    "recall":    round(rpt[cat]["recall"]    * 100, 2),
                    "f1_score":  round(rpt[cat]["f1-score"]  * 100, 2),
                    "support":   int(rpt[cat]["support"]),
                }
                for cat in categories if cat in rpt
            },
        }
        fitted[name] = clf
        print(f"    [{name}] acc={results[name]['accuracy']}% "
              f"macro-F1={results[name]['macro_f1']}% "
              f"CV={results[name]['cv_mean_accuracy']}±{results[name]['cv_std']}%")

    return results, fitted, tfidf, len(X_tr_raw), len(X_te_raw)


def _top_features(tfidf, fitted, categories, n=15):
    """Top n TF-IDF features per class for interpretable models (SVM, Naive Bayes)."""
    names = tfidf.get_feature_names_out()
    out = {}
    for model_name, clf in fitted.items():
        if hasattr(clf, "coef_"):
            coef = clf.coef_
            if coef.ndim == 1:
                coef = coef[np.newaxis, :]
            out[model_name] = {
                cat: [
                    {"feature": names[j], "weight": round(float(coef[i, j]), 4)}
                    for j in np.argsort(coef[i])[-n:][::-1]
                ]
                for i, cat in enumerate(categories)
            }
        elif hasattr(clf, "feature_log_prob_"):
            lp = clf.feature_log_prob_
            out[model_name] = {
                cat: [
                    {"feature": names[j], "weight": round(float(lp[i, j]), 4)}
                    for j in np.argsort(lp[i])[-n:][::-1]
                ]
                for i, cat in enumerate(categories)
            }
    return out


def _check_leakage(df):
    """Count D2 rows where the Job_Role string appears verbatim in Resume_Text."""
    count = sum(
        str(row["Job_Role"]).lower() in str(row["Resume_Text"]).lower()
        for _, row in df.iterrows()
    )
    total = len(df)
    return {
        "rows_with_label_in_text": count,
        "total_rows": total,
        "leakage_percentage": round(count / total * 100, 1),
    }


def _save_models(fitted, tfidf, label_encoder, prefix):
    os.makedirs(MODEL_DIR, exist_ok=True)
    for name, clf in fitted.items():
        key = name.lower().replace(" ", "_")
        with open(os.path.join(MODEL_DIR, f"{prefix}{key}.pkl"), "wb") as f:
            pickle.dump(clf, f)
    with open(os.path.join(MODEL_DIR, f"{prefix}tfidf.pkl"), "wb") as f:
        pickle.dump(tfidf, f)
    with open(os.path.join(MODEL_DIR, f"{prefix}label_encoder.pkl"), "wb") as f:
        pickle.dump(label_encoder, f)


# ──────────────────────────────────────────────────────────────────────────────
# Public training functions
# ──────────────────────────────────────────────────────────────────────────────

def train_dataset1():
    """Train on AI_Resume_Screening.csv — 4 job role classes."""
    os.makedirs(MODEL_DIR, exist_ok=True)
    if not os.path.exists(D1_CSV):
        raise FileNotFoundError(f"Missing: {D1_CSV}")

    df = pd.read_csv(D1_CSV)
    df["features"] = (
        df["Skills"].fillna("") + " " +
        df["Education"].fillna("") + " " +
        df["Experience (Years)"].astype(str) + " " +
        df["Certifications"].fillna("")
    ).apply(_clean)
    df = df[df["features"].str.len() > 5].reset_index(drop=True)

    le = LabelEncoder()
    y  = le.fit_transform(df["Job Role"])
    categories = le.classes_.tolist()
    texts = df["features"].tolist()

    print(f"  Training… n={len(df)}, classes={categories}")
    results, fitted, tfidf, train_n, test_n = _run_pipeline(texts, y, categories, max_features=3000)
    top = _top_features(tfidf, fitted, categories)
    _save_models(fitted, tfidf, le, prefix="d1_")

    output = {
        "dataset_name":  "AI Resume Screening Dataset",
        "dataset_size":  len(df),
        "train_size":    train_n,
        "test_size":     test_n,
        "feature_count": int(tfidf.get_feature_names_out().shape[0]),
        "categories":    categories,
        "approach":      "Skills + Education + Experience (Years) + Certifications -> TF-IDF (3000 features, bigrams)",
        "results":       results,
        "top_features":  top,
    }
    with open(os.path.join(MODEL_DIR, "results_dataset1.json"), "w") as f:
        json.dump(output, f, indent=2)
    return output


def train_dataset2(variant="raw"):
    """Train on resume_dataset_2.csv — 5 job role classes. variant='raw'|'clean'."""
    os.makedirs(MODEL_DIR, exist_ok=True)
    if not os.path.exists(D2_CSV):
        raise FileNotFoundError(f"Missing: {D2_CSV}")

    df = pd.read_csv(D2_CSV, encoding="utf-8-sig")
    df["Resume_Text"] = df["Resume_Text"].fillna("")
    remove = (variant == "clean")
    df["features"] = df["Resume_Text"].apply(lambda t: _clean_d2(t, remove_roles=remove))
    df = df[df["features"].str.len() > 5].reset_index(drop=True)

    le = LabelEncoder()
    y  = le.fit_transform(df["Job_Role"])
    categories = le.classes_.tolist()
    texts = df["features"].tolist()

    print(f"  Training… n={len(df)}, classes={categories}, remove_roles={remove}")
    results, fitted, tfidf, train_n, test_n = _run_pipeline(texts, y, categories, max_features=5000)
    top = _top_features(tfidf, fitted, categories)

    if variant == "raw":
        _save_models(fitted, tfidf, le, prefix="d2_")

    output = {
        "dataset_name":         f"Resume Dataset 2 ({variant})",
        "variant":              variant,
        "dataset_size":         len(df),
        "train_size":           train_n,
        "test_size":            test_n,
        "feature_count":        int(tfidf.get_feature_names_out().shape[0]),
        "categories":           categories,
        "role_strings_removed": remove,
        "approach":             (
            "Resume_Text -> TF-IDF (5000 features, bigrams)"
            + (" [role strings removed]" if remove else "")
        ),
        "results":       results,
        "top_features":  top,
    }
    with open(os.path.join(MODEL_DIR, f"results_dataset2_{variant}.json"), "w") as f:
        json.dump(output, f, indent=2)
    return output


# ──────────────────────────────────────────────────────────────────────────────
# Full evaluation pipeline (called from route + standalone script)
# ──────────────────────────────────────────────────────────────────────────────

def run_full_evaluation():
    """Train D1, check D2 leakage, train D2 raw + clean, generate plots."""
    os.makedirs(MODEL_DIR, exist_ok=True)

    print("=" * 65)
    print("DATASET 1 — AI Resume Screening (1000 rows, 4 job roles)")
    print("=" * 65)
    d1 = train_dataset1()
    _print_results(d1)

    print("\n" + "=" * 65)
    print("DATASET 2 — LEAKAGE CHECK")
    print("=" * 65)
    df2 = pd.read_csv(D2_CSV, encoding="utf-8-sig")
    leakage = _check_leakage(df2)
    print(f"  Rows where Job_Role appears verbatim in Resume_Text: "
          f"{leakage['rows_with_label_in_text']} / {leakage['total_rows']} "
          f"({leakage['leakage_percentage']}%)")

    print("\n" + "=" * 65)
    print("DATASET 2 RAW — Resume_Text (includes role strings)")
    print("=" * 65)
    d2_raw = train_dataset2(variant="raw")
    _print_results(d2_raw)

    print("\n" + "=" * 65)
    print("DATASET 2 CLEAN — role strings removed from Resume_Text")
    print("=" * 65)
    d2_clean = train_dataset2(variant="clean")
    _print_results(d2_clean)

    combined = {
        "dataset1":       d1,
        "dataset2":       d2_raw,     # raw version displayed in frontend tab
        "dataset2_raw":   d2_raw,
        "dataset2_clean": d2_clean,
        "leakage_check":  leakage,
        "cv_metric_note": "cv_mean_accuracy stores 5-fold cross-validated macro-F1 (not accuracy)",
    }
    with open(os.path.join(MODEL_DIR, "evaluation_results.json"), "w") as f:
        json.dump(combined, f, indent=2)

    _print_summary(d1, d2_raw, d2_clean)
    _generate_plots(d1, d2_raw, d2_clean, leakage)

    return combined


# ──────────────────────────────────────────────────────────────────────────────
# Console output helpers
# ──────────────────────────────────────────────────────────────────────────────

def _print_results(data):
    r = data["results"]
    print(f"\n  {data['dataset_name']} | n={data['dataset_size']} | "
          f"train={data['train_size']} | test={data['test_size']} | "
          f"features={data['feature_count']}")
    print(f"  Classes: {data['categories']}\n")
    hdr = f"  {'Model':<16} {'Acc':>7} {'W-F1':>7} {'M-F1':>7} {'M-Pre':>7} {'M-Rec':>7}  {'CV-F1(5k)':>14}  {'Train':>7}"
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for m in _MODEL_KEYS:
        v = r[m]
        cv = f"{v['cv_mean_accuracy']:.2f}±{v['cv_std']:.2f}%"
        print(f"  {m:<16} {v['accuracy']:>6.2f}% {v['f1_score']:>6.2f}% "
              f"{v['macro_f1']:>6.2f}% {v['macro_precision']:>6.2f}% "
              f"{v['macro_recall']:>6.2f}%  {cv:>14}  {v['train_time_seconds']:>6.3f}s")
    if "SVM" in data.get("top_features", {}):
        print("\n  Top TF-IDF features per class (SVM):")
        for cat, feats in data["top_features"]["SVM"].items():
            feat_str = ", ".join(f["feature"] for f in feats[:8])
            print(f"    {cat}: {feat_str}")


def _print_summary(d1, d2_raw, d2_clean):
    print("\n" + "=" * 65)
    print("SUMMARY — MACRO-F1 ACROSS ALL DATASETS & SETTINGS")
    print("=" * 65)
    print(f"  {'Model':<16} {'D1':>8} {'D2-raw':>8} {'D2-clean':>9} {'Leakage Diff':>12}")
    print("  " + "-" * 58)
    for m in _MODEL_KEYS:
        d1f  = d1["results"][m]["macro_f1"]
        d2rf = d2_raw["results"][m]["macro_f1"]
        d2cf = d2_clean["results"][m]["macro_f1"]
        delta = d2rf - d2cf
        print(f"  {m:<16} {d1f:>7.2f}% {d2rf:>7.2f}% {d2cf:>8.2f}% {delta:>+10.2f}%")
    best_d1  = max(_MODEL_KEYS, key=lambda m: d1["results"][m]["macro_f1"])
    best_d2c = max(_MODEL_KEYS, key=lambda m: d2_clean["results"][m]["macro_f1"])
    print(f"\n  Recommendation:")
    print(f"    D1 best:       {best_d1} — macro-F1 {d1['results'][best_d1]['macro_f1']}%")
    print(f"    D2 best (clean): {best_d2c} — macro-F1 {d2_clean['results'][best_d2c]['macro_f1']}%")


# ──────────────────────────────────────────────────────────────────────────────
# Plot generation
# ──────────────────────────────────────────────────────────────────────────────

def _generate_plots(d1, d2_raw, d2_clean, leakage):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  matplotlib not installed — skipping plots.")
        return

    os.makedirs(PLOT_DIR, exist_ok=True)
    colors = {
        "SVM": "#4f46e5", "Random Forest": "#059669",
        "KNN": "#d97706", "Naive Bayes": "#dc2626",
    }
    x = np.arange(len(_MODEL_KEYS))

    # (a) Grouped bar — macro-F1 per model per dataset
    fig, ax = plt.subplots(figsize=(11, 5))
    w = 0.22
    for i, (lbl, ds) in enumerate([
        ("D1: AI Screening", d1),
        ("D2: Resume (raw)", d2_raw),
        ("D2: Resume (clean)", d2_clean),
    ]):
        vals = [ds["results"][m]["macro_f1"] for m in _MODEL_KEYS]
        bars = ax.bar(x + i * w, vals, w, label=lbl, alpha=0.85)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, v + 0.5,
                    f"{v:.1f}", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(x + w)
    ax.set_xticklabels(_MODEL_KEYS)
    ax.set_ylabel("Macro-F1 (%)")
    ax.set_title("Macro-F1 Score — All Models & Datasets")
    ax.set_ylim(0, 115)
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, "macro_f1_comparison.png"), dpi=150)
    plt.close()

    # (b) Confusion matrix heatmaps — best model per dataset
    for ds_label, ds in [("dataset1", d1), ("dataset2_clean", d2_clean)]:
        best = max(_MODEL_KEYS, key=lambda m: ds["results"][m]["macro_f1"])
        cm   = np.array(ds["results"][best]["confusion_matrix"])
        cats = ds["categories"]
        n    = len(cats)
        fig, ax = plt.subplots(figsize=(max(5, n * 1.4), max(4, n * 1.1)))
        im = ax.imshow(cm, cmap="Blues")
        ax.set_xticks(range(n)); ax.set_yticks(range(n))
        ax.set_xticklabels([c[:12] for c in cats], rotation=45, ha="right", fontsize=8)
        ax.set_yticklabels([c[:12] for c in cats], fontsize=8)
        for i in range(n):
            for j in range(n):
                if cm[i, j] > 0:
                    ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=9,
                            color="white" if cm[i, j] > cm.max() * 0.5 else "black")
        ax.set_xlabel("Predicted"); ax.set_ylabel("Actual")
        ax.set_title(f"Confusion Matrix — {best} ({ds['dataset_name']})")
        plt.colorbar(im, ax=ax)
        plt.tight_layout()
        fname = f"cm_{ds_label}_{best.lower().replace(' ', '_')}.png"
        plt.savefig(os.path.join(PLOT_DIR, fname), dpi=150)
        plt.close()

    # (c) 5-fold CV boxplots
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    for ax, (lbl, ds) in zip(axes, [("D1", d1), ("D2 Raw", d2_raw), ("D2 Clean", d2_clean)]):
        cv_data = [ds["results"][m]["cv_scores"] for m in _MODEL_KEYS]
        bp = ax.boxplot(cv_data, patch_artist=True)
        ax.set_xticklabels([m.replace(" ", "\n") for m in _MODEL_KEYS])
        for patch, m in zip(bp["boxes"], _MODEL_KEYS):
            patch.set_facecolor(colors[m]); patch.set_alpha(0.7)
        ax.set_title(f"5-Fold CV Macro-F1 — {lbl}")
        ax.set_ylabel("Macro-F1 (%)")
        ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, "cv_boxplots.png"), dpi=150)
    plt.close()

    # (d) D2 leakage impact
    fig, ax = plt.subplots(figsize=(9, 5))
    w = 0.35
    raw_vals   = [d2_raw  ["results"][m]["macro_f1"] for m in _MODEL_KEYS]
    clean_vals = [d2_clean["results"][m]["macro_f1"] for m in _MODEL_KEYS]
    bars1 = ax.bar(x - w / 2, raw_vals,   w, label="Raw (with role strings)",      alpha=0.85, color="#f59e0b")
    bars2 = ax.bar(x + w / 2, clean_vals, w, label="Clean (role strings removed)", alpha=0.85, color="#3b82f6")
    for bar in list(bars1) + list(bars2):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.4,
                f"{bar.get_height():.1f}", ha="center", va="bottom", fontsize=8.5)
    ax.set_xticks(x); ax.set_xticklabels(_MODEL_KEYS)
    ax.set_ylabel("Macro-F1 (%)")
    ax.set_title(
        f"Dataset 2: Label Leakage Impact on Macro-F1\n"
        f"({leakage['rows_with_label_in_text']}/{leakage['total_rows']} rows affected, "
        f"{leakage['leakage_percentage']}%)"
    )
    ax.legend(); ax.set_ylim(0, 115)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOT_DIR, "d2_leakage_comparison.png"), dpi=150)
    plt.close()

    print(f"\n  Plots saved -> {PLOT_DIR}")
    for fname in [
        "macro_f1_comparison.png", "cv_boxplots.png",
        "d2_leakage_comparison.png",
        f"cm_dataset1_{max(_MODEL_KEYS, key=lambda m: d1['results'][m]['macro_f1']).lower().replace(' ', '_')}.png",
        f"cm_dataset2_clean_{max(_MODEL_KEYS, key=lambda m: d2_clean['results'][m]['macro_f1']).lower().replace(' ', '_')}.png",
    ]:
        print(f"    {fname}")


# ──────────────────────────────────────────────────────────────────────────────
# API helpers
# ──────────────────────────────────────────────────────────────────────────────

def get_evaluation_results():
    """Load combined evaluation JSON for the /results endpoint."""
    path = os.path.join(MODEL_DIR, "evaluation_results.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


def classify_resume(resume_text, dataset=1):
    """Classify a resume using the trained Dataset 1 models (4 IT job roles).

    Called by matcher.py during live matching (dataset=1 always).
    """
    prefix = "d1_" if dataset == 1 else "d2_"
    try:
        with open(os.path.join(MODEL_DIR, f"{prefix}tfidf.pkl"), "rb") as f:
            tfidf = pickle.load(f)
        with open(os.path.join(MODEL_DIR, f"{prefix}label_encoder.pkl"), "rb") as f:
            le = pickle.load(f)
    except FileNotFoundError:
        raise Exception(f"Dataset {dataset} models not trained yet.")

    X = tfidf.transform([_clean(resume_text)])
    predictions = {}
    for name in _MODEL_KEYS:
        key  = name.lower().replace(" ", "_")
        path = os.path.join(MODEL_DIR, f"{prefix}{key}.pkl")
        if not os.path.exists(path):
            continue
        with open(path, "rb") as f:
            clf = pickle.load(f)
        pred_idx   = clf.predict(X)[0]
        category   = le.inverse_transform([pred_idx])[0]
        confidence = None
        if hasattr(clf, "predict_proba"):
            confidence = round(float(clf.predict_proba(X)[0].max()) * 100, 1)
        predictions[name] = {"category": category, "confidence": confidence}
    return predictions
