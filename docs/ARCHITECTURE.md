# 🏗️ System Architecture

## Overview

The Smart Agriculture System follows a layered architecture that cleanly
separates concerns: API layer, business logic, ML inference, and data storage.

The system integrates two ML capabilities:
1. **Crop Recommendation** — Tabular input → Random Forest → Crop predictions
2. **Plant Disease Detection** — Image input → MobileNetV2 → Disease classification

```
┌──────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                             │
│        (Postman / Swagger UI / curl / future Android)        │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTP (JSON / multipart)
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                      API LAYER                               │
│           Django REST Framework Views                        │
│           ├── Input Validation (Serializers)                 │
│           ├── Request/Response Formatting                    │
│           └── Error Handling                                 │
└────────────┬───────────────────────────────┬─────────────────┘
             │                               │
             ▼                               ▼
┌─────────────────────────┐   ┌──────────────────────────────┐
│  CROP RECOMMENDATION    │   │   DISEASE DETECTION          │
│  (Service Layer)        │   │   (Inference Module)         │
│  ├── Feature Vector     │   │   ├── Image Preprocessing    │
│  ├── Model Inference    │   │   ├── MobileNetV2 Inference  │
│  └── Top-3 Ranking      │   │   ├── Class Mapping          │
│                         │   │   └── Top-3 Ranking           │
└────────────┬────────────┘   └────────────┬─────────────────┘
             │                              │
             ▼                              ▼
┌─────────────────────────┐   ┌──────────────────────────────┐
│     ML MODEL LAYER      │   │      ML MODEL LAYER          │
│  (Loaded at startup)    │   │  (Loaded on first request)   │
│  ├── Random Forest      │   │  ├── MobileNetV2 (.keras)    │
│  ├── Feature Metadata   │   │  ├── Class Mapping (.json)   │
│  └── Joblib Artifact    │   │  └── Model Metadata (.json)  │
└─────────────────────────┘   └──────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│                       DATA LAYER                             │
│                Django ORM / SQLite                            │
│                ├── Crop                                       │
│                ├── CropRecommendationRequest                  │
│                └── CropRecommendationResult                   │
└──────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### API Layer (`crop_recommendation/views.py`)
- Receives HTTP requests from clients
- Delegates input validation to DRF serializers
- Routes to the appropriate ML service (recommendation or disease detection)
- Returns formatted JSON responses with consistent envelope
- **Does NOT contain business logic**

### Crop Recommendation Service (`crop_recommendation/services/predictor.py`)
- Loads and caches the trained Random Forest model (singleton pattern)
- Validates input parameters against reasonable ranges
- Constructs feature vectors in the correct order
- Runs model inference
- Ranks predictions and returns top 3 recommendations
- Stores results in the database

### Disease Detection Module (`ml/disease/inference/predictor.py`)
- Loads and caches the trained MobileNetV2 model and class mappings
- Accepts an image file path
- Resizes and preprocesses the image (224×224, MobileNetV2 normalization)
- Runs inference and extracts top-3 predictions
- Maps class indices to crop/disease/status using metadata
- Returns structured prediction results

### ML Pipelines (`ml/`)
- **Crop Recommendation:**
  - Preprocessing → Training → Evaluation → Artifacts
  - Algorithm: Random Forest (scikit-learn)
- **Disease Detection:**
  - Dataset prep → 3-stage training → Evaluation → Artifacts
  - Algorithm: MobileNetV2 (TensorFlow/Keras)

### Data Layer (Django ORM)
- `Crop`: Stores crop information for the API
- `CropRecommendationRequest`: Logs recommendation inputs
- `CropRecommendationResult`: Logs recommendation outputs with scores

## Design Principles

1. **Separation of Concerns**: ML logic is separate from Django views
2. **Single Source of Truth**: Feature order and model paths defined in config files
3. **Load Once, Predict Many**: Models loaded once and cached in memory
4. **API Versioning**: `/api/v1/` from day one
5. **Graceful Degradation**: Disease module import failure is caught gracefully — the server still runs, and the endpoint returns a clear error

## Future Extension

- 📱 Android Application — Kotlin + Jetpack Compose
- 👤 User Authentication & Profiles
- 📊 Advanced Analytics Dashboard
- 🔄 TensorFlow Lite conversion for on-device mobile inference
