# ML Pipeline — Smart Agriculture System

## Overview

This directory contains the complete machine learning pipeline for crop recommendation.

## Structure

```
ml/
├── config.py              # Central configuration (feature order, random seed, paths)
├── data/
│   └── processed/         # Cleaned/processed datasets
├── preprocessing/
│   └── preprocess.py      # Data validation, cleaning, and preprocessing
├── training/
│   ├── train.py           # Main training pipeline (Random Forest)
│   └── compare_models.py  # Multi-model comparison (RF, DT, KNN, XGBoost)
├── evaluation/
│   ├── evaluate.py        # Model evaluation metrics
│   ├── confusion_matrix.py # Confusion matrix generation
│   └── results/           # Saved evaluation outputs
├── inference/
│   └── predictor.py       # Standalone ML prediction (outside Django)
├── artifacts/
│   ├── crop_recommendation_model.joblib  # Trained model (generated)
│   └── feature_metadata.json             # Feature definitions
└── README.md              # This file
```

## Usage

### Train the model

```bash
python ml/training/train.py
```

### Compare models

```bash
python ml/training/compare_models.py
```

### Evaluate the model

```bash
python ml/evaluation/evaluate.py
```

## Configuration

All ML constants are defined in `ml/config.py`:
- Feature order (single source of truth)
- Random state for reproducibility
- File paths
- Hyperparameters
- Validation ranges

**Never hard-code these values in individual scripts. Always import from `ml.config`.**

## Dataset

The raw dataset should be placed in `data/raw/` at the project root.
See `docs/DATASET.md` for dataset documentation.
