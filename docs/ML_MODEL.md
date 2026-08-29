# 🤖 ML Model Documentation

This document describes the machine learning models used in the Smart Agriculture System.

---

## 1. Crop Recommendation Model

This model suggests the best crop to plant based on soil and environmental parameters.

### Overview

| Field            | Value                      |
|------------------|----------------------------|
| **Algorithm**    | Random Forest Classifier   |
| **Library**      | scikit-learn               |
| **Features**     | 7 (N, P, K, temperature, humidity, ph, rainfall) |
| **Target**       | Crop label (22 classes)    |
| **Output**       | Top 3 crops with model scores |

### Hyperparameters

Defined in `ml/config.py`:

```python
RF_PARAMS = {
    'n_estimators': 100,
    'max_depth': 15,
    'min_samples_split': 5,
    'min_samples_leaf': 2,
    'max_features': 'sqrt',
    'random_state': 42,
    'n_jobs': -1,
}
```

---

## 2. Plant Disease Detection Model

This model identifies crop diseases from leaf images using a transfer learning approach.

### Overview

| Field            | Value                      |
|------------------|----------------------------|
| **Algorithm**    | MobileNetV2 (Transfer Learning) |
| **Library**      | TensorFlow / Keras         |
| **Input**        | RGB Image (224 x 224 x 3)  |
| **Target**       | 38 Classes (Healthy & Diseased) |
| **Output**       | Class probabilities (Top 3 returned by API) |
| **Total Params** | ~2.3M                      |
| **File Size**    | ~33.2 MB                   |

### Training Strategy

The model was fine-tuned in three stages to prevent destructive updates to the pretrained ImageNet weights:

1. **Baseline Training:** The MobileNetV2 backbone was frozen entirely. Only the final dense classification head was trained.
2. **Class-Weighted Training:** Class weights were introduced to address imbalances in the PlantVillage dataset.
3. **Fine-Tuning:** The final 30 layers of the MobileNetV2 backbone were un-frozen with a very small learning rate (`1e-5`). **Batch Normalization layers remained frozen** to maintain their learned moving averages and variances.

### Performance Metrics (Final Test Set)

| Metric | Value |
|--------|-------|
| Accuracy | 0.9705 |
| Macro F1 | 0.9657 |
| Weighted F1 | 0.9706 |

For per-class performance details, refer to `ml/disease/evaluation/classification_report.txt`.

---

## ⚠️ Disclaimer

These models provide recommendations and predictions based on statistical patterns learned from historical and curated datasets.
- They do **not** guarantee crop success.
- They do **not** replace professional agricultural or agronomic advice.
- The model scores represent predicted probabilities from the classifiers and should not be interpreted as absolute certainty.
