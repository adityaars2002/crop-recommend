"""
ML Pipeline Configuration — Single Source of Truth.

This module defines all constants used across the ML pipeline.
Import from here instead of hard-coding values in individual scripts.

Usage:
    from ml.config import FEATURE_ORDER, RANDOM_STATE, TARGET_COLUMN
"""

from pathlib import Path

# ==============================================================================
# PATHS
# ==============================================================================

# Root of the project (crop-recomend/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ML directories
ML_DIR = Path(__file__).resolve().parent
ML_DATA_RAW_DIR = PROJECT_ROOT / 'data' / 'raw'
ML_DATA_PROCESSED_DIR = PROJECT_ROOT / 'data' / 'processed'
ML_ARTIFACTS_DIR = ML_DIR / 'artifacts'
ML_EVALUATION_RESULTS_DIR = ML_DIR / 'evaluation' / 'results'
ML_ANALYSIS_DIR = ML_DIR / 'analysis'
ML_ANALYSIS_PLOTS_DIR = ML_ANALYSIS_DIR / 'plots'

# Model artifact paths
MODEL_PATH = ML_ARTIFACTS_DIR / 'crop_recommendation_model.joblib'
METADATA_PATH = ML_ARTIFACTS_DIR / 'feature_metadata.json'

# ==============================================================================
# DATASET
# ==============================================================================

# Expected dataset filename
DATASET_FILENAME = 'Crop_recommendation.csv'
DATASET_PATH = ML_DATA_RAW_DIR / DATASET_FILENAME
PROCESSED_DATASET_FILENAME = 'crop_recommendation_clean.csv'
PROCESSED_DATASET_PATH = ML_DATA_PROCESSED_DIR / PROCESSED_DATASET_FILENAME
DATASET_SUMMARY_PATH = ML_DATA_PROCESSED_DIR / 'dataset_summary.json'

# ==============================================================================
# FEATURES — SINGLE SOURCE OF TRUTH
# ==============================================================================
# The order of features MUST remain consistent everywhere:
# data preprocessing, model training, prediction service, and API.

FEATURE_ORDER = [
    'N',            # Nitrogen content in soil
    'P',            # Phosphorus content in soil
    'K',            # Potassium content in soil
    'temperature',  # Temperature in °C
    'humidity',     # Relative humidity in %
    'ph',           # Soil pH (0-14)
    'rainfall',     # Rainfall in mm
]

# Target variable
TARGET_COLUMN = 'label'

# ==============================================================================
# MODEL TRAINING
# ==============================================================================

# Fixed random seed for reproducibility
RANDOM_STATE = 42

# Train/test split ratio
TEST_SIZE = 0.2

# Model version (update when retraining with significant changes)
MODEL_VERSION = '1.0'

# ==============================================================================
# VALIDATION RANGES
# ==============================================================================
# Reasonable ranges for input validation.
# These are not strict agricultural limits — they serve as sanity checks
# to reject clearly impossible values.

FEATURE_RANGES = {
    'N':           {'min': 0, 'max': 200,  'unit': 'kg/ha'},
    'P':           {'min': 0, 'max': 200,  'unit': 'kg/ha'},
    'K':           {'min': 0, 'max': 300,  'unit': 'kg/ha'},
    'temperature': {'min': -10, 'max': 60, 'unit': '°C'},
    'humidity':    {'min': 0, 'max': 100,  'unit': '%'},
    'ph':          {'min': 0, 'max': 14,   'unit': ''},
    'rainfall':    {'min': 0, 'max': 500,  'unit': 'mm'},
}

# ==============================================================================
# RANDOM FOREST HYPERPARAMETERS
# ==============================================================================
# Reasonable parameters for a crop recommendation model.
# These are not the result of exhaustive tuning — they are chosen to
# balance accuracy, training speed, and interpretability.

RF_PARAMS = {
    'n_estimators': 100,
    'max_depth': 15,
    'min_samples_split': 5,
    'min_samples_leaf': 2,
    'max_features': 'sqrt',
    'random_state': RANDOM_STATE,
    'n_jobs': -1,  # Use all available CPU cores
}
