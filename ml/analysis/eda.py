"""
Exploratory Data Analysis (EDA) for the Crop Recommendation Dataset.

This module generates:
- Basic dataset statistics and summary report
- Missing value analysis
- Duplicate analysis
- Data type validation
- Range and validity checks
- Outlier analysis with boxplots
- Class distribution chart
- Feature distribution histograms
- Correlation heatmap
- Feature vs crop analysis

All plots are saved to ml/analysis/plots/.
All reports are printed to console and returned as structured data.

Usage:
    python ml/analysis/eda.py
"""

import sys
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving plots
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure project root is on sys.path
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from ml.config import (
    FEATURE_ORDER,
    TARGET_COLUMN,
    FEATURE_RANGES,
    ML_ANALYSIS_PLOTS_DIR,
    ML_DATA_PROCESSED_DIR,
    DATASET_SUMMARY_PATH,
)
from ml.data_loader import load_raw_dataset


# ==============================================================================
# REPORT GENERATION
# ==============================================================================

def generate_basic_report(df: pd.DataFrame) -> dict:
    """
    Generate a basic summary report of the dataset.

    Returns a dict with dataset dimensions, dtypes, missing values, etc.
    """
    report = {
        'rows': int(df.shape[0]),
        'columns': int(df.shape[1]),
        'column_names': list(df.columns),
        'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
        'features': FEATURE_ORDER,
        'target': TARGET_COLUMN,
    }

    print("=" * 60)
    print("DATASET BASIC REPORT")
    print("=" * 60)
    print(f"  Rows:    {report['rows']}")
    print(f"  Columns: {report['columns']}")
    print(f"  Columns: {report['column_names']}")
    print()
    print("  Data Types:")
    for col, dtype in report['dtypes'].items():
        print(f"    {col:15s}  {dtype}")
    print()

    return report


def analyze_missing_values(df: pd.DataFrame) -> dict:
    """Analyze and report missing values in each column."""
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)

    result = {}
    print("=" * 60)
    print("MISSING VALUE ANALYSIS")
    print("=" * 60)
    print(f"  {'Column':<15s}  {'Missing':>8s}  {'Percentage':>10s}")
    print(f"  {'-'*15}  {'-'*8}  {'-'*10}")

    for col in df.columns:
        count = int(missing[col])
        pct = float(missing_pct[col])
        result[col] = {'count': count, 'percentage': pct}
        print(f"  {col:<15s}  {count:>8d}  {pct:>9.2f}%")

    total_missing = int(missing.sum())
    print(f"\n  Total missing values: {total_missing}")

    if total_missing == 0:
        print("  [OK] No missing values found.")
    else:
        print("  [!] Missing values detected - review cleaning decisions.")

    print()
    return result


def analyze_duplicates(df: pd.DataFrame) -> dict:
    """Analyze and report duplicate rows."""
    num_duplicates = int(df.duplicated().sum())
    total_rows = len(df)

    print("=" * 60)
    print("DUPLICATE ANALYSIS")
    print("=" * 60)
    print(f"  Total rows:      {total_rows}")
    print(f"  Duplicate rows:  {num_duplicates}")
    print(f"  Unique rows:     {total_rows - num_duplicates}")

    if num_duplicates == 0:
        print("  [OK] No duplicate rows found.")
    else:
        pct = num_duplicates / total_rows * 100
        print(f"  [!] {num_duplicates} duplicate rows ({pct:.2f}%) detected.")

    print()
    return {'duplicate_count': num_duplicates, 'total_rows': total_rows}


def analyze_data_types(df: pd.DataFrame) -> dict:
    """Validate data types for all columns."""
    print("=" * 60)
    print("DATA TYPE VALIDATION")
    print("=" * 60)

    issues = []
    result = {}

    for col in FEATURE_ORDER:
        dtype = str(df[col].dtype)
        is_numeric = pd.api.types.is_numeric_dtype(df[col])
        status = "[OK] numeric" if is_numeric else "[X] NOT numeric"
        result[col] = {'dtype': dtype, 'is_numeric': is_numeric}
        print(f"  {col:<15s}  {dtype:<10s}  {status}")
        if not is_numeric:
            issues.append(col)

    # Target column
    target_dtype = str(df[TARGET_COLUMN].dtype)
    is_categorical = not pd.api.types.is_numeric_dtype(df[TARGET_COLUMN])
    status = "[OK] categorical" if is_categorical else "[X] NOT categorical"
    result[TARGET_COLUMN] = {'dtype': target_dtype, 'is_categorical': is_categorical}
    print(f"  {TARGET_COLUMN:<15s}  {target_dtype:<10s}  {status}")

    if issues:
        print(f"\n  [!] Non-numeric feature columns: {issues}")
    else:
        print(f"\n  [OK] All feature columns are numeric, target is categorical.")

    print()
    return result


def analyze_ranges(df: pd.DataFrame) -> dict:
    """Perform range and validity checks on numerical features."""
    print("=" * 60)
    print("RANGE AND VALIDITY CHECKS")
    print("=" * 60)

    result = {}
    issues = []

    for col in FEATURE_ORDER:
        stats = {
            'min': float(df[col].min()),
            'max': float(df[col].max()),
            'mean': float(df[col].mean()),
            'median': float(df[col].median()),
            'q1': float(df[col].quantile(0.25)),
            'q3': float(df[col].quantile(0.75)),
            'std': float(df[col].std()),
        }
        result[col] = stats

        col_range = FEATURE_RANGES.get(col, {})
        expected_min = col_range.get('min', None)
        expected_max = col_range.get('max', None)
        unit = col_range.get('unit', '')

        print(f"\n  {col} ({unit}):")
        print(f"    Min:    {stats['min']:.4f}")
        print(f"    Q1:     {stats['q1']:.4f}")
        print(f"    Median: {stats['median']:.4f}")
        print(f"    Q3:     {stats['q3']:.4f}")
        print(f"    Max:    {stats['max']:.4f}")
        print(f"    Mean:   {stats['mean']:.4f}")
        print(f"    Std:    {stats['std']:.4f}")

        # Check for negative values where not expected
        if expected_min is not None:
            below_min = int((df[col] < expected_min).sum())
            if below_min > 0:
                issues.append(f"{col}: {below_min} values below {expected_min}")
                print(f"    [!] {below_min} values below expected minimum ({expected_min})")

        if expected_max is not None:
            above_max = int((df[col] > expected_max).sum())
            if above_max > 0:
                issues.append(f"{col}: {above_max} values above {expected_max}")
                print(f"    [!] {above_max} values above expected maximum ({expected_max})")

        # Check for NaN/Inf
        nan_count = int(df[col].isna().sum())
        inf_count = int(np.isinf(df[col]).sum()) if pd.api.types.is_numeric_dtype(df[col]) else 0
        if nan_count > 0:
            issues.append(f"{col}: {nan_count} NaN values")
        if inf_count > 0:
            issues.append(f"{col}: {inf_count} Inf values")

    if issues:
        print(f"\n  [!] Issues found:")
        for issue in issues:
            print(f"    - {issue}")
    else:
        print(f"\n  [OK] All values within expected ranges.")

    print()
    return result


def analyze_class_distribution(df: pd.DataFrame) -> dict:
    """Analyze the target class distribution."""
    class_counts = df[TARGET_COLUMN].value_counts()
    num_classes = int(df[TARGET_COLUMN].nunique())

    print("=" * 60)
    print("CLASS DISTRIBUTION")
    print("=" * 60)
    print(f"  Number of crop classes: {num_classes}")
    print()
    print(f"  {'Crop':<20s}  {'Count':>6s}  {'Percentage':>10s}")
    print(f"  {'-'*20}  {'-'*6}  {'-'*10}")

    result = {}
    for crop, count in class_counts.items():
        pct = count / len(df) * 100
        result[crop] = {'count': int(count), 'percentage': round(float(pct), 2)}
        print(f"  {crop:<20s}  {count:>6d}  {pct:>9.2f}%")

    # Check for class imbalance
    min_count = int(class_counts.min())
    max_count = int(class_counts.max())
    ratio = max_count / min_count if min_count > 0 else float('inf')
    print(f"\n  Min class size: {min_count}")
    print(f"  Max class size: {max_count}")
    print(f"  Imbalance ratio: {ratio:.2f}")

    if ratio > 3:
        print("  [!] Significant class imbalance detected.")
    else:
        print("  [OK] Classes are reasonably balanced.")

    print()
    return {'num_classes': num_classes, 'distribution': result}


def analyze_outliers(df: pd.DataFrame) -> dict:
    """
    Perform IQR-based outlier analysis for numerical features.

    Note: Outliers are identified but NOT automatically removed.
    Tree-based models like Random Forest are generally robust to outliers.
    """
    print("=" * 60)
    print("OUTLIER ANALYSIS (IQR Method)")
    print("=" * 60)

    result = {}
    for col in FEATURE_ORDER:
        q1 = float(df[col].quantile(0.25))
        q3 = float(df[col].quantile(0.75))
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        num_outliers = len(outliers)

        result[col] = {
            'q1': q1,
            'q3': q3,
            'iqr': float(iqr),
            'lower_bound': float(lower_bound),
            'upper_bound': float(upper_bound),
            'outlier_count': num_outliers,
            'outlier_percentage': round(num_outliers / len(df) * 100, 2),
        }

        status = f"[!] {num_outliers} outliers" if num_outliers > 0 else "[OK] none"
        print(f"  {col:<15s}  IQR={iqr:>8.2f}  "
              f"[{lower_bound:>8.2f}, {upper_bound:>8.2f}]  {status}")

    print()
    print("  Note: Random Forest is generally robust to outliers.")
    print("  Outliers are reported for awareness but not automatically removed.")
    print()

    return result


def compute_basic_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute basic statistics for numerical features."""
    stats = df[FEATURE_ORDER].describe().T
    print("=" * 60)
    print("BASIC STATISTICS")
    print("=" * 60)
    print(stats.to_string())
    print()
    return stats


# ==============================================================================
# PLOT GENERATION
# ==============================================================================

def _ensure_plots_dir():
    """Create the plots directory if it doesn't exist."""
    ML_ANALYSIS_PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def plot_class_distribution(df: pd.DataFrame) -> Path:
    """Generate and save a bar chart of crop class distribution."""
    _ensure_plots_dir()

    class_counts = df[TARGET_COLUMN].value_counts()

    fig, ax = plt.subplots(figsize=(14, 6))
    bars = ax.bar(range(len(class_counts)), class_counts.values, color=sns.color_palette('viridis', len(class_counts)))
    ax.set_xticks(range(len(class_counts)))
    ax.set_xticklabels(class_counts.index, rotation=45, ha='right', fontsize=9)
    ax.set_xlabel('Crop', fontsize=11)
    ax.set_ylabel('Number of Samples', fontsize=11)
    ax.set_title('Crop Class Distribution', fontsize=14, fontweight='bold')

    # Add count labels on bars
    for bar, count in zip(bars, class_counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                str(count), ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    path = ML_ANALYSIS_PLOTS_DIR / 'crop_class_distribution.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  [SAVED] {path}")
    return path


def plot_nutrient_boxplots(df: pd.DataFrame) -> Path:
    """Generate boxplots for nutrient features (N, P, K)."""
    _ensure_plots_dir()

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    nutrient_cols = ['N', 'P', 'K']

    for ax, col in zip(axes, nutrient_cols):
        sns.boxplot(y=df[col], ax=ax, color='lightblue', flierprops={'markersize': 3})
        ax.set_title(f'{col} Distribution', fontsize=12, fontweight='bold')
        ax.set_ylabel(col, fontsize=10)

    fig.suptitle('Nutrient Feature Boxplots', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    path = ML_ANALYSIS_PLOTS_DIR / 'nutrient_boxplots.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  [SAVED] {path}")
    return path


def plot_environment_boxplots(df: pd.DataFrame) -> Path:
    """Generate boxplots for environmental features (temperature, humidity, ph, rainfall)."""
    _ensure_plots_dir()

    fig, axes = plt.subplots(1, 4, figsize=(16, 5))
    env_cols = ['temperature', 'humidity', 'ph', 'rainfall']

    for ax, col in zip(axes, env_cols):
        sns.boxplot(y=df[col], ax=ax, color='lightgreen', flierprops={'markersize': 3})
        ax.set_title(f'{col.capitalize()} Distribution', fontsize=12, fontweight='bold')
        ax.set_ylabel(col, fontsize=10)

    fig.suptitle('Environmental Feature Boxplots', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    path = ML_ANALYSIS_PLOTS_DIR / 'environment_boxplots.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  [SAVED] {path}")
    return path


def plot_feature_distributions(df: pd.DataFrame) -> Path:
    """Generate histograms for all numerical features."""
    _ensure_plots_dir()

    fig, axes = plt.subplots(2, 4, figsize=(18, 10))
    axes = axes.flatten()

    for i, col in enumerate(FEATURE_ORDER):
        ax = axes[i]
        ax.hist(df[col], bins=30, color='steelblue', edgecolor='white', alpha=0.8)
        ax.set_title(f'{col}', fontsize=12, fontweight='bold')
        ax.set_xlabel(col, fontsize=9)
        ax.set_ylabel('Frequency', fontsize=9)

    # Hide the unused 8th subplot
    axes[7].set_visible(False)

    fig.suptitle('Feature Distributions', fontsize=14, fontweight='bold')
    plt.tight_layout()
    path = ML_ANALYSIS_PLOTS_DIR / 'feature_distributions.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  [SAVED] {path}")
    return path


def plot_correlation_heatmap(df: pd.DataFrame) -> Path:
    """Generate a correlation heatmap for numerical features."""
    _ensure_plots_dir()

    corr = df[FEATURE_ORDER].corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(
        corr,
        mask=mask,
        annot=True,
        fmt='.2f',
        cmap='coolwarm',
        center=0,
        vmin=-1,
        vmax=1,
        square=True,
        linewidths=0.5,
        ax=ax,
    )
    ax.set_title('Feature Correlation Heatmap', fontsize=14, fontweight='bold')

    plt.tight_layout()
    path = ML_ANALYSIS_PLOTS_DIR / 'correlation_heatmap.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  [SAVED] {path}")
    return path


def plot_features_by_crop(df: pd.DataFrame) -> Path:
    """
    Generate boxplots of each feature grouped by crop.
    Creates a grid of subplots showing how features vary across crop classes.
    """
    _ensure_plots_dir()

    fig, axes = plt.subplots(len(FEATURE_ORDER), 1, figsize=(16, 4 * len(FEATURE_ORDER)))

    for i, col in enumerate(FEATURE_ORDER):
        ax = axes[i]
        # Sort crops by median value for better readability
        crop_medians = df.groupby(TARGET_COLUMN)[col].median().sort_values()
        crop_order = crop_medians.index.tolist()

        sns.boxplot(
            data=df,
            x=TARGET_COLUMN,
            y=col,
            order=crop_order,
            ax=ax,
            palette='viridis',
            flierprops={'markersize': 2},
        )
        ax.set_title(f'{col} by Crop', fontsize=12, fontweight='bold')
        ax.set_xlabel('')
        ax.set_ylabel(col, fontsize=10)
        ax.tick_params(axis='x', rotation=45, labelsize=8)

    fig.suptitle('Feature Distributions by Crop Class', fontsize=16, fontweight='bold', y=1.01)
    plt.tight_layout()
    path = ML_ANALYSIS_PLOTS_DIR / 'features_by_crop.png'
    fig.savefig(path, dpi=120, bbox_inches='tight')
    plt.close(fig)
    print(f"  [SAVED] {path}")
    return path


# ==============================================================================
# DATASET SUMMARY JSON
# ==============================================================================

def generate_dataset_summary(df: pd.DataFrame, missing_info: dict,
                              duplicate_info: dict, class_info: dict) -> dict:
    """Generate and save a dataset summary JSON."""
    ML_DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    summary = {
        'rows': int(df.shape[0]),
        'columns': int(df.shape[1]),
        'features': FEATURE_ORDER,
        'target': TARGET_COLUMN,
        'number_of_classes': class_info.get('num_classes', 0),
        'crop_classes': sorted(df[TARGET_COLUMN].unique().tolist()),
        'missing_values': {col: info['count'] for col, info in missing_info.items()},
        'duplicate_rows': duplicate_info.get('duplicate_count', 0),
        'statistics': {},
    }

    # Add basic stats for each feature
    for col in FEATURE_ORDER:
        summary['statistics'][col] = {
            'min': round(float(df[col].min()), 4),
            'max': round(float(df[col].max()), 4),
            'mean': round(float(df[col].mean()), 4),
            'std': round(float(df[col].std()), 4),
        }

    with open(DATASET_SUMMARY_PATH, 'w') as f:
        json.dump(summary, f, indent=4)

    print(f"  [SAVED] {DATASET_SUMMARY_PATH}")
    return summary


# ==============================================================================
# MAIN EDA RUNNER
# ==============================================================================

def run_eda() -> dict:
    """
    Run the complete EDA pipeline.

    Returns a dict containing all analysis results.
    """
    print()
    print("=" * 60)
    print("   EXPLORATORY DATA ANALYSIS - Crop Recommendation")
    print("=" * 60)
    print()

    # Load dataset
    print("[INFO] Loading raw dataset...")
    df = load_raw_dataset()
    print(f"[INFO] Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    print()

    # Run analyses
    basic_report = generate_basic_report(df)
    basic_stats = compute_basic_statistics(df)
    missing_info = analyze_missing_values(df)
    duplicate_info = analyze_duplicates(df)
    dtype_info = analyze_data_types(df)
    range_info = analyze_ranges(df)
    outlier_info = analyze_outliers(df)
    class_info = analyze_class_distribution(df)

    # Generate plots
    print("=" * 60)
    print("GENERATING PLOTS")
    print("=" * 60)
    plot_class_distribution(df)
    plot_nutrient_boxplots(df)
    plot_environment_boxplots(df)
    plot_feature_distributions(df)
    plot_correlation_heatmap(df)
    plot_features_by_crop(df)
    print()

    # Generate summary JSON
    print("=" * 60)
    print("GENERATING DATASET SUMMARY")
    print("=" * 60)
    summary = generate_dataset_summary(df, missing_info, duplicate_info, class_info)
    print()

    # Compile correlation insights
    corr = df[FEATURE_ORDER].corr()
    print("=" * 60)
    print("CORRELATION INSIGHTS")
    print("=" * 60)
    # Find notable correlations (|r| > 0.3)
    notable = []
    for i, col1 in enumerate(FEATURE_ORDER):
        for j, col2 in enumerate(FEATURE_ORDER):
            if i < j:
                r = corr.loc[col1, col2]
                if abs(r) > 0.3:
                    notable.append((col1, col2, r))
    if notable:
        for col1, col2, r in sorted(notable, key=lambda x: abs(x[2]), reverse=True):
            direction = "positive" if r > 0 else "negative"
            print(f"  {col1} <-> {col2}: r = {r:.3f} ({direction})")
    else:
        print("  No strong correlations (|r| > 0.3) found among features.")
    print("  Note: Correlation does not imply causation.")
    print()

    print("=" * 60)
    print("EDA COMPLETE")
    print("=" * 60)

    return {
        'basic_report': basic_report,
        'missing_info': missing_info,
        'duplicate_info': duplicate_info,
        'dtype_info': dtype_info,
        'range_info': range_info,
        'outlier_info': outlier_info,
        'class_info': class_info,
        'summary': summary,
    }


if __name__ == '__main__':
    run_eda()
