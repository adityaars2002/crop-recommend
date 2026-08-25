"""
Data Preprocessing Pipeline for Crop Recommendation.

This module provides the complete preprocessing pipeline:
1. Load raw dataset
2. Validate schema
3. Analyze data quality (missing values, duplicates, types, ranges)
4. Clean dataset (remove duplicates, handle invalid values)
5. Save processed dataset
6. Generate analysis reports and plots
7. Generate data quality report

Usage:
    python ml/preprocessing/preprocess.py

All decisions are documented. No data is silently deleted.
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

# Ensure project root is on sys.path
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from ml.config import (
    FEATURE_ORDER,
    TARGET_COLUMN,
    FEATURE_RANGES,
    ML_DATA_PROCESSED_DIR,
    PROCESSED_DATASET_PATH,
    DATASET_SUMMARY_PATH,
)
from ml.data_loader import load_raw_dataset, validate_schema, DatasetError, DatasetValidationError
from ml.analysis.eda import run_eda

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
)
logger = logging.getLogger(__name__)


# ==============================================================================
# CLEANING FUNCTIONS
# ==============================================================================

def remove_duplicates(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """
    Remove exact duplicate rows from the dataset.

    Returns:
        tuple: (cleaned DataFrame, number of duplicates removed)

    Decision: Exact duplicates in a dataset of this nature are likely
    data entry errors or repeated observations. Removing them prevents
    artificial bias toward certain samples.
    """
    num_before = len(df)
    df_clean = df.drop_duplicates().reset_index(drop=True)
    num_removed = num_before - len(df_clean)

    if num_removed > 0:
        logger.info(f"Removed {num_removed} exact duplicate rows.")
        logger.info(f"  Before: {num_before} rows -> After: {len(df_clean)} rows")
    else:
        logger.info("No duplicate rows to remove.")

    return df_clean, num_removed


def handle_missing_values(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Handle missing values in the dataset.

    Strategy:
    - For the target column (label): remove rows with missing labels
      (no valid training target exists without a label).
    - For feature columns: report missing values.
      For this dataset, missing values are not expected.
      If any exist, they are reported and the rows are dropped
      (since the dataset is small and imputation could introduce bias).

    Returns:
        tuple: (cleaned DataFrame, dict with cleaning info)
    """
    info = {'rows_removed': 0, 'details': {}}

    # Check target column
    missing_target = df[TARGET_COLUMN].isna().sum()
    if missing_target > 0:
        logger.info(f"Removing {missing_target} rows with missing target ('{TARGET_COLUMN}').")
        logger.info(f"  Reason: No valid training target without a crop label.")
        df = df.dropna(subset=[TARGET_COLUMN])
        info['rows_removed'] += int(missing_target)
        info['details']['target_missing'] = int(missing_target)

    # Check feature columns
    for col in FEATURE_ORDER:
        missing_count = df[col].isna().sum()
        if missing_count > 0:
            logger.info(f"Removing {missing_count} rows with missing values in '{col}'.")
            df = df.dropna(subset=[col])
            info['rows_removed'] += int(missing_count)
            info['details'][col] = int(missing_count)

    if info['rows_removed'] == 0:
        logger.info("No missing values to handle.")
    else:
        df = df.reset_index(drop=True)

    return df, info


def validate_value_ranges(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Validate feature values against reasonable ranges.

    Strategy: Report out-of-range values but keep them unless they are
    clearly erroneous. The FEATURE_RANGES in config define sanity-check
    boundaries, not strict agricultural limits.

    Returns:
        tuple: (DataFrame, dict with validation results)
    """
    info = {'issues': [], 'rows_flagged': 0}

    for col in FEATURE_ORDER:
        ranges = FEATURE_RANGES.get(col, {})
        expected_min = ranges.get('min')
        expected_max = ranges.get('max')

        if expected_min is not None:
            below = df[df[col] < expected_min]
            if len(below) > 0:
                msg = f"{col}: {len(below)} values below {expected_min} (min found: {df[col].min():.4f})"
                info['issues'].append(msg)
                info['rows_flagged'] += len(below)
                logger.warning(msg)

        if expected_max is not None:
            above = df[df[col] > expected_max]
            if len(above) > 0:
                msg = f"{col}: {len(above)} values above {expected_max} (max found: {df[col].max():.4f})"
                info['issues'].append(msg)
                info['rows_flagged'] += len(above)
                logger.warning(msg)

        # Check for NaN/Inf
        nan_count = int(df[col].isna().sum())
        inf_count = int(np.isinf(df[col]).sum())
        if nan_count > 0:
            info['issues'].append(f"{col}: {nan_count} NaN values")
        if inf_count > 0:
            info['issues'].append(f"{col}: {inf_count} Inf values")
            # Remove Inf values as they are clearly invalid
            df = df[~np.isinf(df[col])]
            logger.info(f"Removed {inf_count} rows with Inf values in '{col}'.")

    if not info['issues']:
        logger.info("All feature values are within expected ranges.")
    else:
        logger.info(f"Range validation found {len(info['issues'])} potential issue(s).")
        logger.info("Note: Values outside expected ranges are kept unless clearly erroneous.")
        logger.info("Tree-based models like Random Forest are generally robust to outliers.")

    return df, info


def ensure_feature_order(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure the dataset columns are in the canonical feature order.

    The final processed dataset columns will be:
    [N, P, K, temperature, humidity, ph, rainfall, label]
    """
    expected_columns = FEATURE_ORDER + [TARGET_COLUMN]
    df = df[expected_columns].copy()
    return df


# ==============================================================================
# SAVE FUNCTIONS
# ==============================================================================

def save_processed_dataset(df: pd.DataFrame) -> Path:
    """Save the cleaned dataset to data/processed/."""
    ML_DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df.to_csv(PROCESSED_DATASET_PATH, index=False)
    logger.info(f"Saved processed dataset: {PROCESSED_DATASET_PATH}")
    logger.info(f"  Shape: {df.shape[0]} rows x {df.shape[1]} columns")

    return PROCESSED_DATASET_PATH


def generate_quality_report(
    df_raw: pd.DataFrame,
    df_clean: pd.DataFrame,
    eda_results: dict,
    duplicate_info: dict,
    missing_info: dict,
    range_info: dict,
) -> Path:
    """Generate the data quality report as a Markdown document."""
    docs_dir = _project_root / 'docs'
    docs_dir.mkdir(parents=True, exist_ok=True)
    report_path = docs_dir / 'DATA_QUALITY_REPORT.md'

    # Gather information
    class_info = eda_results.get('class_info', {})
    outlier_info = eda_results.get('outlier_info', {})
    summary = eda_results.get('summary', {})
    range_analysis = eda_results.get('range_info', {})

    # Class distribution text
    class_dist_lines = []
    dist = class_info.get('distribution', {})
    for crop, info in sorted(dist.items()):
        class_dist_lines.append(
            f"| {crop:<20s} | {info['count']:>6d} | {info['percentage']:>9.2f}% |"
        )

    # Outlier summary text
    outlier_lines = []
    for col, info in outlier_info.items():
        outlier_lines.append(
            f"| {col:<15s} | {info['outlier_count']:>6d} | {info['outlier_percentage']:>9.2f}% "
            f"| [{info['lower_bound']:.2f}, {info['upper_bound']:.2f}] |"
        )

    # Range summary text
    range_lines = []
    for col, stats in range_analysis.items():
        range_lines.append(
            f"| {col:<15s} | {stats['min']:>10.4f} | {stats['q1']:>10.4f} "
            f"| {stats['median']:>10.4f} | {stats['q3']:>10.4f} | {stats['max']:>10.4f} |"
        )

    # Missing values text
    missing_eda = eda_results.get('missing_info', {})
    missing_lines = []
    for col, info in missing_eda.items():
        missing_lines.append(f"| {col:<15s} | {info['count']:>8d} | {info['percentage']:>9.2f}% |")

    report = f"""# 📊 Data Quality Report

> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Dataset Overview

| Property | Value |
|----------|-------|
| **Dataset Name** | Crop Recommendation Dataset |
| **Source** | [Kaggle - atharvaingle/crop-recommendation-dataset](https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset) |
| **Raw Records** | {len(df_raw)} |
| **Clean Records** | {len(df_clean)} |
| **Features** | {len(FEATURE_ORDER)} numerical features |
| **Target** | `{TARGET_COLUMN}` (crop name) |
| **Crop Classes** | {class_info.get('num_classes', 'N/A')} |

## Dataset Source

- **Name:** Crop Recommendation Dataset
- **Author:** Atharva Ingle
- **Platform:** Kaggle
- **URL:** https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset
- **Format:** CSV
- **License:** CC0: Public Domain (as listed on Kaggle)

## Features

| Feature | Description | Unit | Type |
|---------|-------------|------|------|
| `N` | Nitrogen content in soil | kg/ha | Float |
| `P` | Phosphorus content in soil | kg/ha | Float |
| `K` | Potassium content in soil | kg/ha | Float |
| `temperature` | Average temperature | °C | Float |
| `humidity` | Relative humidity | % | Float |
| `ph` | Soil pH value | 0-14 | Float |
| `rainfall` | Annual rainfall | mm | Float |
| `label` | Recommended crop (target) | — | String |

## Missing Values

| Column | Missing | Percentage |
|--------|---------|------------|
{chr(10).join(missing_lines)}

{"✓ No missing values found in the dataset." if all(info['count'] == 0 for info in missing_eda.values()) else "⚠ Missing values were found and handled (see Cleaning Decisions)."}

## Duplicate Records

| Property | Value |
|----------|-------|
| **Raw dataset rows** | {len(df_raw)} |
| **Duplicate rows** | {duplicate_info.get('rows_removed', 0)} |
| **After deduplication** | {len(df_clean)} |

{f"**Decision:** {duplicate_info.get('rows_removed', 0)} exact duplicate rows were removed." if duplicate_info.get('rows_removed', 0) > 0 else "✓ No duplicate rows found."}

## Data Types

All 7 feature columns are numeric (float64), and the target column (`label`) is categorical (object/string). ✓

## Feature Statistics

| Feature | Min | Q1 | Median | Q3 | Max |
|---------|-----|-----|--------|-----|-----|
{chr(10).join(range_lines)}

## Invalid Values

{chr(10).join(f"- {issue}" for issue in range_info.get('issues', [])) if range_info.get('issues') else "✓ No invalid values (NaN, Inf, or clearly erroneous values) detected."}

## Outlier Analysis

Outliers identified using the IQR method (1.5 × IQR rule):

| Feature | Outliers | Percentage | IQR Bounds |
|---------|----------|------------|------------|
{chr(10).join(outlier_lines)}

**Decision:** Outliers are **not removed**. Random Forest is a tree-based algorithm that is
generally robust to outliers. The identified outliers appear to be valid observations within
the natural variability of agricultural data.

## Class Distribution

| Crop | Count | Percentage |
|------|-------|------------|
{chr(10).join(class_dist_lines)}

{"✓ Classes are reasonably balanced." if class_info.get('num_classes', 0) > 0 and max(info['count'] for info in dist.values()) / min(info['count'] for info in dist.values()) <= 3 else "⚠ Some class imbalance detected."}

## Correlation Analysis

Notable correlations among features (|r| > 0.3) are reported in the correlation heatmap.
See: `ml/analysis/plots/correlation_heatmap.png`

**Note:** Correlation does not imply causation.

## Cleaning Decisions

| Decision | Rationale |
|----------|-----------|
| Remove exact duplicates | Prevents artificial bias toward repeated samples |
| Keep outliers | Random Forest is robust to outliers; values appear valid |
| No feature scaling | Not required for tree-based models |
| No label encoding | Scikit-learn handles string targets via LabelEncoder internally |
| Preserve column order | Feature order maintained as: N, P, K, temperature, humidity, ph, rainfall |

## Final Dataset

| Property | Value |
|----------|-------|
| **Location** | `data/processed/crop_recommendation_clean.csv` |
| **Rows** | {len(df_clean)} |
| **Columns** | {df_clean.shape[1]} |
| **Column Order** | `{', '.join(FEATURE_ORDER + [TARGET_COLUMN])}` |

## Limitations

1. The dataset contains a limited number of crop classes (22) and may not represent all crops grown globally.
2. Environmental parameters are averages and do not capture seasonal or micro-climate variations.
3. Soil composition (N, P, K) is represented as single values, not considering soil depth or spatial variability.
4. The dataset does not include other potentially important factors like soil texture, irrigation, elevation, or sunlight hours.
5. The model recommendations are based on patterns in the training data and should not be treated as definitive agricultural advice.

## Generated Files

| File | Description |
|------|-------------|
| `data/processed/crop_recommendation_clean.csv` | Cleaned dataset |
| `data/processed/dataset_summary.json` | Dataset summary statistics |
| `ml/analysis/plots/crop_class_distribution.png` | Class distribution bar chart |
| `ml/analysis/plots/nutrient_boxplots.png` | N, P, K boxplots |
| `ml/analysis/plots/environment_boxplots.png` | Temperature, humidity, pH, rainfall boxplots |
| `ml/analysis/plots/feature_distributions.png` | Feature histograms |
| `ml/analysis/plots/correlation_heatmap.png` | Feature correlation heatmap |
| `ml/analysis/plots/features_by_crop.png` | Feature distributions per crop |
"""

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    logger.info(f"Saved data quality report: {report_path}")
    return report_path


# ==============================================================================
# MAIN PIPELINE
# ==============================================================================

def run_preprocessing_pipeline():
    """
    Run the complete preprocessing pipeline.

    Steps:
    1. Load raw dataset
    2. Validate schema
    3. Run EDA (analysis + plots)
    4. Clean dataset (duplicates, missing values, range checks)
    5. Enforce feature order
    6. Save processed dataset
    7. Generate quality report
    """
    print()
    print("=" * 60)
    print("   PREPROCESSING PIPELINE - Crop Recommendation")
    print("=" * 60)
    print()

    # Step 1: Load raw dataset
    logger.info("Loading raw dataset...")
    try:
        df_raw = load_raw_dataset()
    except (DatasetError, DatasetValidationError) as e:
        logger.error(str(e))
        sys.exit(1)

    logger.info(f"Dataset loaded: {df_raw.shape[0]} rows, {df_raw.shape[1]} columns")

    # Step 2: Validate schema (already done in load_raw_dataset, but explicit)
    logger.info("Validating schema...")
    try:
        validate_schema(df_raw)
        logger.info("Schema validation successful.")
    except DatasetValidationError as e:
        logger.error(str(e))
        sys.exit(1)

    # Step 3: Run EDA
    logger.info("Running exploratory data analysis...")
    eda_results = run_eda()

    # Step 4: Clean dataset
    print()
    print("=" * 60)
    print("   DATA CLEANING")
    print("=" * 60)
    print()

    df_clean = df_raw.copy()

    # 4a: Remove duplicates
    logger.info("Checking for duplicate rows...")
    df_clean, dup_info = remove_duplicates(df_clean)

    # 4b: Handle missing values
    logger.info("Handling missing values...")
    df_clean, miss_info = handle_missing_values(df_clean)

    # 4c: Validate value ranges
    logger.info("Validating value ranges...")
    df_clean, range_info = validate_value_ranges(df_clean)

    # Step 5: Enforce feature order
    logger.info("Enforcing canonical feature order...")
    df_clean = ensure_feature_order(df_clean)
    logger.info(f"Final column order: {list(df_clean.columns)}")

    # Step 6: Save processed dataset
    logger.info("Saving processed dataset...")
    save_processed_dataset(df_clean)

    # Step 7: Generate quality report
    logger.info("Generating data quality report...")
    report_path = generate_quality_report(
        df_raw=df_raw,
        df_clean=df_clean,
        eda_results=eda_results,
        duplicate_info={'rows_removed': dup_info},
        missing_info=miss_info,
        range_info=range_info,
    )

    # Final summary
    print()
    print("=" * 60)
    print("   PREPROCESSING COMPLETE")
    print("=" * 60)
    print()
    logger.info(f"Raw dataset:       {df_raw.shape[0]} rows")
    logger.info(f"Processed dataset: {df_clean.shape[0]} rows")
    logger.info(f"Rows removed:      {df_raw.shape[0] - df_clean.shape[0]}")
    logger.info(f"Crop classes:      {df_clean[TARGET_COLUMN].nunique()}")
    logger.info(f"")
    logger.info(f"Output files:")
    logger.info(f"  Processed data:  {PROCESSED_DATASET_PATH}")
    logger.info(f"  Summary JSON:    {DATASET_SUMMARY_PATH}")
    logger.info(f"  Quality report:  {report_path}")
    logger.info(f"  Plots:           ml/analysis/plots/")
    logger.info(f"")
    logger.info(f"Phase 2 preprocessing completed successfully.")

    return df_clean


if __name__ == '__main__':
    run_preprocessing_pipeline()
