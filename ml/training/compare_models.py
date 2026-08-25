"""
Model Comparison Script for Crop Recommendation.

This script evaluates multiple machine learning models using 5-fold 
Stratified Cross-Validation on the training set (80%). The 20% test 
set is held out completely.

Models evaluated:
- Random Forest
- Decision Tree
- K-Nearest Neighbors (with scaling)
- Logistic Regression (with scaling)

Usage:
    python ml/training/compare_models.py
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import make_scorer, accuracy_score, precision_score, recall_score, f1_score

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
)
from ml.data_loader import load_processed_dataset

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def prepare_data(df: pd.DataFrame):
    """Separate features and target, and perform train/test split."""
    X = df[FEATURE_ORDER]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    
    return X_train, X_test, y_train, y_test


def get_models() -> dict:
    """Return a dictionary of models/pipelines to evaluate."""
    return {
        'Random Forest': RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1),
        'Decision Tree': DecisionTreeClassifier(random_state=RANDOM_STATE),
        'KNN': Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', KNeighborsClassifier())
        ]),
        'Logistic Regression': Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', LogisticRegression(max_iter=2000, random_state=RANDOM_STATE, n_jobs=-1))
        ])
    }


def compare_models(X_train: pd.DataFrame, y_train: pd.Series) -> pd.DataFrame:
    """Evaluate all models using Stratified K-Fold CV."""
    models = get_models()
    results = []

    # Define CV strategy
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    # Define scoring metrics
    scoring = {
        'accuracy': 'accuracy',
        'f1_weighted': make_scorer(f1_score, average='weighted'),
        'precision_weighted': make_scorer(precision_score, average='weighted', zero_division=0),
        'recall_weighted': make_scorer(recall_score, average='weighted', zero_division=0)
    }

    print("\nEvaluating models using 5-Fold Stratified CV:")
    print("-" * 75)
    print(f"{'Model':<22} | {'Accuracy':<15} | {'F1 (Weighted)':<15} | {'Fit Time (s)':<10}")
    print("-" * 75)

    for name, model in models.items():
        # Run cross-validation
        cv_results = cross_validate(
            model, X_train, y_train, cv=cv, scoring=scoring, 
            n_jobs=-1, return_train_score=False
        )

        # Calculate means and stds
        acc_mean = cv_results['test_accuracy'].mean()
        acc_std = cv_results['test_accuracy'].std()
        f1_mean = cv_results['test_f1_weighted'].mean()
        f1_std = cv_results['test_f1_weighted'].std()
        prec_mean = cv_results['test_precision_weighted'].mean()
        rec_mean = cv_results['test_recall_weighted'].mean()
        time_mean = cv_results['fit_time'].mean()

        print(f"{name:<22} | {acc_mean:.4f} ± {acc_std:.4f} | {f1_mean:.4f} ± {f1_std:.4f} | {time_mean:.3f}")

        results.append({
            'Model': name,
            'CV_Accuracy_Mean': acc_mean,
            'CV_Accuracy_Std': acc_std,
            'CV_F1_Mean': f1_mean,
            'CV_F1_Std': f1_std,
            'CV_Precision_Mean': prec_mean,
            'CV_Recall_Mean': rec_mean,
            'Fit_Time_Mean': time_mean
        })

    print("-" * 75)
    return pd.DataFrame(results)


def plot_comparison(results_df: pd.DataFrame, output_dir: Path):
    """Create and save a bar chart comparing model accuracies."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Sort by accuracy descending
    results_df = results_df.sort_values('CV_Accuracy_Mean', ascending=False)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot bars
    bars = sns.barplot(
        data=results_df, 
        x='CV_Accuracy_Mean', 
        y='Model', 
        palette='viridis',
        ax=ax,
        capsize=0.1,
        err_kws={'linewidth': 1.5}
    )
    
    # Add error bars manually since seaborn's barplot doesn't take std directly easily
    for i, (_, row) in enumerate(results_df.iterrows()):
        ax.errorbar(row['CV_Accuracy_Mean'], i, xerr=row['CV_Accuracy_Std'], color='black', capsize=5, lw=1.5)
        # Add text label
        ax.text(row['CV_Accuracy_Mean'] / 2, i, f"{row['CV_Accuracy_Mean']:.4f}", 
                ha='center', va='center', color='white', fontweight='bold')
    
    ax.set_title('Model Comparison - Cross-Validation Accuracy', fontsize=14, fontweight='bold')
    ax.set_xlabel('Mean CV Accuracy', fontsize=12)
    ax.set_ylabel('')
    ax.set_xlim(0, 1.05)  # Leave space for error bars
    
    plt.tight_layout()
    plot_path = output_dir / 'model_comparison.png'
    fig.savefig(plot_path, dpi=150)
    plt.close(fig)
    logger.info(f"Saved comparison plot to {plot_path}")


def save_results(results_df: pd.DataFrame, output_dir: Path):
    """Save results to CSV and JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save CSV
    csv_path = output_dir / 'model_comparison.csv'
    results_df.to_csv(csv_path, index=False)
    logger.info(f"Saved comparison CSV to {csv_path}")
    
    # Save JSON
    json_path = output_dir / 'model_comparison.json'
    json_data = {
        'timestamp': datetime.now().isoformat(),
        'models': results_df.to_dict(orient='records')
    }
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=4)
    logger.info(f"Saved comparison JSON to {json_path}")


def main():
    logger.info("Starting model comparison pipeline...")
    
    try:
        df = load_processed_dataset()
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        sys.exit(1)
        
    X_train, X_test, y_train, y_test = prepare_data(df)
    logger.info(f"Training set: {X_train.shape[0]} samples (80%)")
    logger.info(f"Test set: {X_test.shape[0]} samples (20%) - HELD OUT")
    
    results_df = compare_models(X_train, y_train)
    
    save_results(results_df, ML_EVALUATION_RESULTS_DIR)
    plot_comparison(results_df, ML_EVALUATION_RESULTS_DIR)
    
    best_model = results_df.loc[results_df['CV_Accuracy_Mean'].idxmax()]
    logger.info(f"\nBest Model: {best_model['Model']} (Accuracy: {best_model['CV_Accuracy_Mean']:.4f})")
    logger.info("Model comparison completed successfully.")

if __name__ == '__main__':
    main()
