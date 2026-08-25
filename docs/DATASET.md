# Dataset Documentation

## Dataset Information

| Property | Value |
|----------|-------|
| **Name** | Crop Recommendation Dataset |
| **Author** | Atharva Ingle |
| **Source** | [Kaggle](https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset) |
| **Mirror** | [GitHub - AbhishekKandoi](https://github.com/AbhishekKandoi/Crop-Yield-Prediction-based-on-Indian-Agriculture) |
| **Samples** | 2200 |
| **Features** | 7 numerical features |
| **Classes** | 22 crop types |
| **Target** | `label` (crop name) |
| **Format** | CSV |
| **License** | CC0: Public Domain (as listed on Kaggle) |
| **Date Downloaded** | August 2026 |

## Features

| Feature | Description | Unit | Data Type |
|---------|-------------|------|-----------|
| `N` | Nitrogen content in soil | kg/ha | Integer |
| `P` | Phosphorus content in soil | kg/ha | Integer |
| `K` | Potassium content in soil | kg/ha | Integer |
| `temperature` | Average temperature | Celsius | Float |
| `humidity` | Relative humidity | % | Float |
| `ph` | Soil pH value | 0-14 | Float |
| `rainfall` | Annual rainfall | mm | Float |

## Target Variable

| Field | Description | Type | Unique Values |
|-------|-------------|------|---------------|
| `label` | Recommended crop name | String | 22 |

## Crop Classes

The dataset contains 100 samples for each of the following 22 crops:

apple, banana, blackgram, chickpea, coconut, coffee, cotton, grapes, jute, kidneybeans, lentil, maize, mango, mothbeans, mungbean, muskmelon, orange, papaya, pigeonpeas, pomegranate, rice, watermelon

## Preprocessing

The following preprocessing was performed (see `docs/DATA_QUALITY_REPORT.md` for full details):

1. **Schema Validation**: Verified all 8 required columns exist with correct data types.
2. **Missing Values**: No missing values found (0 across all columns).
3. **Duplicates**: No exact duplicate rows found.
4. **Range Validation**: All values within expected physical ranges.
5. **Outlier Analysis**: Outliers identified via IQR method but **not removed** (Random Forest is robust to outliers).
6. **Feature Order**: Columns reordered to canonical order: N, P, K, temperature, humidity, ph, rainfall, label.

## File Locations

| File | Path | Description |
|------|------|-------------|
| Raw dataset | `data/raw/Crop_recommendation.csv` | Original, unmodified dataset |
| Clean dataset | `data/processed/crop_recommendation_clean.csv` | Preprocessed dataset |
| Summary JSON | `data/processed/dataset_summary.json` | Dataset statistics |
| Quality report | `docs/DATA_QUALITY_REPORT.md` | Full data quality analysis |

## Usage Notes

- The raw dataset in `data/raw/` must **never be modified** directly.
- All cleaning operations produce a new file in `data/processed/`.
- The feature order is defined in `ml/config.py` as the single source of truth.
- To regenerate the processed dataset: `python ml/preprocessing/preprocess.py`
