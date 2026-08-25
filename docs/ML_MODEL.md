# 🤖 ML Model Documentation

> **Status**: Will be completed after Phase 4 (ML Evaluation).

## Model

| Field            | Value                      |
|------------------|----------------------------|
| **Algorithm**    | Random Forest Classifier   |
| **Library**      | scikit-learn               |
| **Features**     | 7 (N, P, K, temperature, humidity, ph, rainfall) |
| **Target**       | Crop label (22 classes)    |
| **Output**       | Top 3 crops with model scores |

## Hyperparameters

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

## Performance Metrics

> Will be populated after model training in Phase 3-4.

## Disclaimer

This model provides recommendations based on patterns learned from the training
dataset. It does not guarantee crop success. The model scores represent predicted
probabilities from the Random Forest classifier and should not be interpreted as
scientifically validated confidence values.
