# 📊 Data Quality Report

> Generated: 2026-08-25 16:21:47

## Dataset Overview

| Property | Value |
|----------|-------|
| **Dataset Name** | Crop Recommendation Dataset |
| **Source** | [Kaggle - atharvaingle/crop-recommendation-dataset](https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset) |
| **Raw Records** | 2200 |
| **Clean Records** | 2200 |
| **Features** | 7 numerical features |
| **Target** | `label` (crop name) |
| **Crop Classes** | 22 |

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
| N               |        0 |      0.00% |
| P               |        0 |      0.00% |
| K               |        0 |      0.00% |
| temperature     |        0 |      0.00% |
| humidity        |        0 |      0.00% |
| ph              |        0 |      0.00% |
| rainfall        |        0 |      0.00% |
| label           |        0 |      0.00% |

✓ No missing values found in the dataset.

## Duplicate Records

| Property | Value |
|----------|-------|
| **Raw dataset rows** | 2200 |
| **Duplicate rows** | 0 |
| **After deduplication** | 2200 |

✓ No duplicate rows found.

## Data Types

All 7 feature columns are numeric (float64), and the target column (`label`) is categorical (object/string). ✓

## Feature Statistics

| Feature | Min | Q1 | Median | Q3 | Max |
|---------|-----|-----|--------|-----|-----|
| N               |     0.0000 |    21.0000 |    37.0000 |    84.2500 |   140.0000 |
| P               |     5.0000 |    28.0000 |    51.0000 |    68.0000 |   145.0000 |
| K               |     5.0000 |    20.0000 |    32.0000 |    49.0000 |   205.0000 |
| temperature     |     8.8257 |    22.7694 |    25.5987 |    28.5617 |    43.6755 |
| humidity        |    14.2580 |    60.2620 |    80.4731 |    89.9488 |    99.9819 |
| ph              |     3.5048 |     5.9717 |     6.4250 |     6.9236 |     9.9351 |
| rainfall        |    20.2113 |    64.5517 |    94.8676 |   124.2675 |   298.5601 |

## Invalid Values

✓ No invalid values (NaN, Inf, or clearly erroneous values) detected.

## Outlier Analysis

Outliers identified using the IQR method (1.5 × IQR rule):

| Feature | Outliers | Percentage | IQR Bounds |
|---------|----------|------------|------------|
| N               |      0 |      0.00% | [-73.88, 179.12] |
| P               |    138 |      6.27% | [-32.00, 128.00] |
| K               |    200 |      9.09% | [-23.50, 92.50] |
| temperature     |     86 |      3.91% | [14.08, 37.25] |
| humidity        |     30 |      1.36% | [15.73, 134.48] |
| ph              |     57 |      2.59% | [4.54, 8.35] |
| rainfall        |    100 |      4.55% | [-25.02, 213.84] |

**Decision:** Outliers are **not removed**. Random Forest is a tree-based algorithm that is
generally robust to outliers. The identified outliers appear to be valid observations within
the natural variability of agricultural data.

## Class Distribution

| Crop | Count | Percentage |
|------|-------|------------|
| apple                |    100 |      4.55% |
| banana               |    100 |      4.55% |
| blackgram            |    100 |      4.55% |
| chickpea             |    100 |      4.55% |
| coconut              |    100 |      4.55% |
| coffee               |    100 |      4.55% |
| cotton               |    100 |      4.55% |
| grapes               |    100 |      4.55% |
| jute                 |    100 |      4.55% |
| kidneybeans          |    100 |      4.55% |
| lentil               |    100 |      4.55% |
| maize                |    100 |      4.55% |
| mango                |    100 |      4.55% |
| mothbeans            |    100 |      4.55% |
| mungbean             |    100 |      4.55% |
| muskmelon            |    100 |      4.55% |
| orange               |    100 |      4.55% |
| papaya               |    100 |      4.55% |
| pigeonpeas           |    100 |      4.55% |
| pomegranate          |    100 |      4.55% |
| rice                 |    100 |      4.55% |
| watermelon           |    100 |      4.55% |

✓ Classes are reasonably balanced.

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
| **Rows** | 2200 |
| **Columns** | 8 |
| **Column Order** | `N, P, K, temperature, humidity, ph, rainfall, label` |

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
