"""
Standalone evaluation script.

Run from the backend/ directory with the venv active:
    python run_evaluation.py

Trains all classifiers on both datasets, runs leakage analysis,
saves evaluation_results.json and PNG plots to data/models/.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.classifier import run_full_evaluation

if __name__ == "__main__":
    run_full_evaluation()
