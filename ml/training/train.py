"""
Final Model Training Script for Crop Recommendation.

This script:
1. Loads the processed dataset and performs train/test split.
2. Performs hyperparameter tuning for Random Forest on the training set.
3. Trains the final model using the best hyperparameters.
4. Evaluates the model on the held-out test set.
5. Generates confusion matrix and feature importance.
6. Saves the final model artifact and metadata.

Usage:
    python ml/training/train.py
"""

import sys
import json
import logging
import joblib
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)

# Ensure project root is on sys.path
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from ml.config import (
    FEATURE_ORDER,
    TARGET_COLUMN,
    RANDOM_STATE,
    TEST_SIZE,
    ML_EVALUATION_RESULTS_DIR,
    ML_ARTIFACTS_DIR,
)
from ml.data_loader import load_processed_dataset

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

MODEL_ARTIFACT_PATH = ML_ARTIFACTS_DIR / 'crop_recommendation_model.joblib'
METADATA_PATH = ML_ARTIFACTS_DIR / 'model_metadata.json'


def prepare_data(df: pd.DataFrame):
    """Separate features and target, and perform train/test split."""
    X = df[FEATURE_ORDER]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    return X_train, X_test, y_train, y_test


def tune_hyperparameters(X_train: pd.DataFrame, y_train: pd.Series) -> RandomForestClassifier:
    """Tune Random Forest hyperparameters using RandomizedSearchCV."""
    logger.info("Starting hyperparameter tuning on training set...")
    
    # Base model
    rf = RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1)
    
    # Moderate search grid
    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [None, 10, 20, 30],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
        'max_features': ['sqrt', 'log2']
    }
    
    # Randomized Search to save time (10 iterations * 3 folds = 30 fits)
    search = RandomizedSearchCV(
        estimator=rf,
        param_distributions=param_grid,
        n_iter=10,
        cv=3,
        scoring='accuracy',
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbose=1
    )
    
    search.fit(X_train, y_train)
    logger.info(f"Best parameters found: {search.best_params_}")
    
    # Save best parameters
    ML_EVALUATION_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    best_params_path = ML_EVALUATION_RESULTS_DIR / 'best_parameters.json'
    with open(best_params_path, 'w') as f:
        json.dump({
            'model': 'RandomForestClassifier',
            'parameters': search.best_params_,
            'cv_accuracy': search.best_score_
        }, f, indent=4)
        
    return search.best_estimator_


def evaluate_model(model, X_test: pd.DataFrame, y_test: pd.Series, labels: list):
    """Evaluate model on test set and save metrics."""
    logger.info("Evaluating final model on test set...")
    
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    metrics = {
        'model': 'RandomForestClassifier',
        'accuracy': accuracy_score(y_test, y_pred),
        'precision_weighted': precision_score(y_test, y_pred, average='weighted', zero_division=0),
        'recall_weighted': recall_score(y_test, y_pred, average='weighted', zero_division=0),
        'f1_weighted': f1_score(y_test, y_pred, average='weighted', zero_division=0),
        'precision_macro': precision_score(y_test, y_pred, average='macro', zero_division=0),
        'recall_macro': recall_score(y_test, y_pred, average='macro', zero_division=0),
        'f1_macro': f1_score(y_test, y_pred, average='macro', zero_division=0)
    }
    
    # Save metrics JSON
    metrics_path = ML_EVALUATION_RESULTS_DIR / 'metrics.json'
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=4)
    logger.info(f"Test Accuracy: {metrics['accuracy']:.4f}")
    
    # Save classification report
    report = classification_report(y_test, y_pred, target_names=labels, zero_division=0)
    report_path = ML_EVALUATION_RESULTS_DIR / 'classification_report.txt'
    with open(report_path, 'w') as f:
        f.write(report)
        
    # Generate and save confusion matrix
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    plot_confusion_matrix(cm, labels)
    
    # Generate and save feature importance
    plot_feature_importance(model)
    
    return metrics


def plot_confusion_matrix(cm: np.ndarray, labels: list):
    """Generate professional confusion matrix visualization."""
    fig, ax = plt.subplots(figsize=(14, 12))
    
    sns.heatmap(
        cm, annot=True, fmt='d', cmap='Blues', 
        xticklabels=labels, yticklabels=labels, ax=ax,
        square=True, cbar_kws={'shrink': .7}
    )
    
    ax.set_title('Confusion Matrix - Crop Recommendation', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('True Crop Class', fontsize=12, fontweight='bold')
    ax.set_xlabel('Predicted Crop Class', fontsize=12, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    plt.tight_layout()
    cm_path = ML_EVALUATION_RESULTS_DIR / 'confusion_matrix.png'
    fig.savefig(cm_path, dpi=150)
    plt.close(fig)
    logger.info(f"Saved confusion matrix to {cm_path}")


def plot_feature_importance(model: RandomForestClassifier):
    """Extract and plot feature importance from Random Forest."""
    importances = model.feature_importances_
    
    # Create DataFrame
    fi_df = pd.DataFrame({
        'feature': FEATURE_ORDER,
        'importance': importances
    }).sort_values('importance', ascending=False).reset_index(drop=True)
    fi_df['rank'] = fi_df.index + 1
    
    # Save CSV
    csv_path = ML_EVALUATION_RESULTS_DIR / 'feature_importance.csv'
    fi_df.to_csv(csv_path, index=False)
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=fi_df, x='importance', y='feature', 
        palette='viridis', ax=ax
    )
    
    ax.set_title('Random Forest Feature Importance', fontsize=14, fontweight='bold')
    ax.set_xlabel('Importance Score', fontsize=12)
    ax.set_ylabel('Feature', fontsize=12)
    
    # Add values on bars
    for i, v in enumerate(fi_df['importance']):
        ax.text(v + 0.005, i, f'{v:.3f}', va='center', fontsize=10)
        
    plt.tight_layout()
    plot_path = ML_EVALUATION_RESULTS_DIR / 'feature_importance.png'
    fig.savefig(plot_path, dpi=150)
    plt.close(fig)
    logger.info(f"Saved feature importance plot to {plot_path}")


def save_model(model: RandomForestClassifier, X_train: pd.DataFrame, y_train: pd.Series, test_metrics: dict):
    """Save the final model and metadata."""
    ML_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save Model
    joblib.dump(model, MODEL_ARTIFACT_PATH)
    logger.info(f"Model saved to {MODEL_ARTIFACT_PATH}")
    
    # Save Metadata
    metadata = {
        "model_name": "RandomForestClassifier",
        "model_version": "1.0.0",
        "features": FEATURE_ORDER,
        "target": TARGET_COLUMN,
        "classes": sorted(y_train.unique().tolist()),
        "training_random_state": RANDOM_STATE,
        "test_size": TEST_SIZE,
        "training_samples": X_train.shape[0],
        "test_samples": int(X_train.shape[0] / (1 - TEST_SIZE) * TEST_SIZE),
        "training_date": datetime.now().isoformat(),
        "hyperparameters": model.get_params(),
        "final_test_metrics": test_metrics
    }
    
    with open(METADATA_PATH, 'w') as f:
        json.dump(metadata, f, indent=4)
    logger.info(f"Model metadata saved to {METADATA_PATH}")


def main():
    logger.info("Starting Final Model Training Pipeline...")
    
    # 1. Load Data
    try:
        df = load_processed_dataset()
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        sys.exit(1)
        
    # 2. Prepare Data
    X_train, X_test, y_train, y_test = prepare_data(df)
    labels = sorted(df[TARGET_COLUMN].unique().tolist())
    
    # 3. Tune Hyperparameters
    best_model = tune_hyperparameters(X_train, y_train)
    
    # 4. Final Training (using best parameters on full training set)
    logger.info("Training final model on complete training set...")
    best_model.fit(X_train, y_train)
    
    # 5. Evaluate on Test Set
    test_metrics = evaluate_model(best_model, X_test, y_test, labels)
    
    # 6. Save Model
    save_model(best_model, X_train, y_train, test_metrics)
    
    logger.info("Training pipeline completed successfully.")

if __name__ == '__main__':
    main()
