"""
Model Evaluation Script for Saved Artifacts.

This script loads a saved model and evaluates it on the exact test set
used during training to verify test metrics reproducibility.

Usage:
    python ml/evaluation/evaluate.py
"""

import sys
import json
import logging
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, classification_report

# Ensure project root is on sys.path
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from ml.inference.predictor import load_model_and_metadata
from ml.data_loader import load_processed_dataset
from ml.training.train import prepare_data

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting model evaluation from saved artifact...")
    
    # 1. Load Model
    try:
        model, metadata = load_model_and_metadata()
        logger.info(f"Loaded model version {metadata.get('model_version', 'unknown')}")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        sys.exit(1)
        
    # 2. Load Data
    try:
        df = load_processed_dataset()
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        sys.exit(1)
        
    # 3. Prepare test set exactly as in training
    # Note: prepare_data uses the config's RANDOM_STATE and TEST_SIZE, 
    # ensuring identical split as long as config hasn't changed.
    _, X_test, _, y_test = prepare_data(df)
    
    # Verify split size matches metadata if available
    expected_samples = metadata.get('test_samples')
    if expected_samples and len(y_test) != expected_samples:
        logger.warning(
            f"Test set size ({len(y_test)}) does not match metadata ({expected_samples}). "
            "The config variables may have changed since the model was trained."
        )
        
    # 4. Predict and evaluate
    logger.info("Evaluating on held-out test set...")
    y_pred = model.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    logger.info(f"Test Accuracy: {acc:.4f}")
    
    classes = metadata.get('classes', sorted(y_test.unique().tolist()))
    report = classification_report(y_test, y_pred, target_names=classes)
    
    print("\n" + "="*55)
    print("CLASSIFICATION REPORT")
    print("="*55)
    print(report)

if __name__ == '__main__':
    main()
