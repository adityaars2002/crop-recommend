"""
Dataset Loader for the Crop Recommendation ML Pipeline.

Provides reusable functions to locate, load, and validate the crop
recommendation dataset. Uses project-relative paths defined in ml.config.

Usage:
    from ml.data_loader import load_raw_dataset, load_processed_dataset

    df = load_raw_dataset()
    df_clean = load_processed_dataset()
"""

import sys
from pathlib import Path

import pandas as pd

# Ensure the project root is on sys.path so ml.config is importable
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from ml.config import (
    DATASET_PATH,
    PROCESSED_DATASET_PATH,
    FEATURE_ORDER,
    TARGET_COLUMN,
)


class DatasetError(Exception):
    """Raised when the dataset cannot be loaded or is invalid."""
    pass


class DatasetValidationError(DatasetError):
    """Raised when the dataset schema validation fails."""
    pass


# All required columns: features + target
REQUIRED_COLUMNS = FEATURE_ORDER + [TARGET_COLUMN]


def load_raw_dataset() -> pd.DataFrame:
    """
    Load the raw crop recommendation dataset from data/raw/.

    Returns:
        pd.DataFrame: The raw dataset.

    Raises:
        DatasetError: If the dataset file is not found.
        DatasetValidationError: If required columns are missing or dataset is empty.
    """
    if not DATASET_PATH.exists():
        raise DatasetError(
            f"Crop recommendation dataset not found.\n"
            f"Expected location:\n  {DATASET_PATH}\n\n"
            f"Please place the dataset CSV file at the location above.\n"
            f"You can download it from:\n"
            f"  https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset"
        )

    df = pd.read_csv(DATASET_PATH)

    if df.empty:
        raise DatasetError("Dataset contains no records.")

    validate_schema(df)

    return df


def load_processed_dataset() -> pd.DataFrame:
    """
    Load the processed (cleaned) dataset from data/processed/.

    Returns:
        pd.DataFrame: The cleaned dataset.

    Raises:
        DatasetError: If the processed dataset file is not found.
    """
    if not PROCESSED_DATASET_PATH.exists():
        raise DatasetError(
            f"Processed dataset not found.\n"
            f"Expected location:\n  {PROCESSED_DATASET_PATH}\n\n"
            f"Run the preprocessing pipeline first:\n"
            f"  python ml/preprocessing/preprocess.py"
        )

    df = pd.read_csv(PROCESSED_DATASET_PATH)
    validate_schema(df)

    return df


def validate_schema(df: pd.DataFrame) -> None:
    """
    Validate that the dataset contains all required columns with correct types.

    Args:
        df: DataFrame to validate.

    Raises:
        DatasetValidationError: If validation fails.
    """
    # Check required columns exist
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise DatasetValidationError(
            f"Dataset schema validation failed.\n"
            f"Missing columns: {missing_cols}\n"
            f"Available columns: {list(df.columns)}"
        )

    # Check feature columns are numeric
    for col in FEATURE_ORDER:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise DatasetValidationError(
                f"Column '{col}' should be numeric but has dtype '{df[col].dtype}'."
            )

    # Check target column contains strings/categories
    if pd.api.types.is_numeric_dtype(df[TARGET_COLUMN]):
        raise DatasetValidationError(
            f"Target column '{TARGET_COLUMN}' should be categorical/string "
            f"but has dtype '{df[TARGET_COLUMN].dtype}'."
        )


if __name__ == '__main__':
    # Quick test: load and validate the raw dataset
    print("[INFO] Testing dataset loader...")
    try:
        df = load_raw_dataset()
        print(f"[INFO] Dataset loaded successfully: {df.shape[0]} rows, {df.shape[1]} columns")
        print(f"[INFO] Columns: {list(df.columns)}")
        print(f"[INFO] Crop classes: {df[TARGET_COLUMN].nunique()}")
        print(f"[INFO] Schema validation passed.")
    except (DatasetError, DatasetValidationError) as e:
        print(f"[ERROR] {e}")
