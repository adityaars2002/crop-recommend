# 🏗️ System Architecture

## Overview

The Smart Agriculture System follows a layered architecture that cleanly
separates concerns: API layer, business logic, ML inference, and data storage.

```
┌──────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                             │
│              (Android App / Swagger UI / curl)               │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTP (JSON)
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                      API LAYER                               │
│           Django REST Framework Views                        │
│           ├── Input Validation (Serializers)                 │
│           ├── Request/Response Formatting                    │
│           └── Error Handling                                 │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                   SERVICE LAYER                              │
│           Prediction Service (predictor.py)                  │
│           ├── Feature Vector Construction                    │
│           ├── Model Inference                                │
│           ├── Result Ranking (Top 3)                         │
│           └── Input Validation                               │
└────────────┬─────────────────────────────┬───────────────────┘
             │                             │
             ▼                             ▼
┌────────────────────────┐   ┌─────────────────────────────────┐
│     ML MODEL LAYER     │   │         DATA LAYER              │
│   (Loaded at startup)  │   │   Django ORM / SQLite           │
│   ├── Random Forest    │   │   ├── Crop                      │
│   ├── Feature Metadata │   │   ├── CropRecommendation        │
│   └── Joblib Artifact  │   │   └── (Future: DiseaseScan)     │
└────────────────────────┘   └─────────────────────────────────┘
```

## Component Responsibilities

### API Layer (`crop_recommendation/views.py`)
- Receives HTTP requests from clients
- Delegates input validation to DRF serializers
- Calls the prediction service
- Returns formatted JSON responses
- **Does NOT contain business logic**

### Service Layer (`crop_recommendation/services/predictor.py`)
- Loads and caches the trained ML model (singleton pattern)
- Validates input parameters against reasonable ranges
- Constructs feature vectors in the correct order
- Runs model inference
- Ranks predictions and returns top 3 recommendations

### ML Pipeline (`ml/`)
- **Preprocessing**: Data validation and cleaning
- **Training**: Model training pipeline (Random Forest)
- **Evaluation**: Metrics generation (accuracy, F1, confusion matrix)
- **Artifacts**: Saved model and metadata files
- **Config**: Single source of truth for feature order, random seed, etc.

### Data Layer (Django ORM)
- `Crop`: Stores crop information for the API
- `CropRecommendation`: Logs recommendation history
- Future: `DiseaseScan` (Phase 2)

## Design Principles

1. **Separation of Concerns**: ML logic is separate from Django views
2. **Single Source of Truth**: Feature order defined once in `ml/config.py`
3. **Load Once, Predict Many**: Model loaded at startup, not per-request
4. **API Versioning**: `/api/v1/` from day one
5. **Extensibility**: Architecture accommodates future disease detection module

## Future Extension

The disease detection module (Phase 2) will:
- Add a `disease_detection/` Django app
- Use on-device ML (LiteRT/TFLite) on the Android side
- Optionally add a server-side fallback API
- Share the same API versioning structure (`/api/v1/diseases/`)
