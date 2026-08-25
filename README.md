# 🌾 Smart Agriculture System — Crop Recommendation

> A machine-learning-powered decision-support system that recommends suitable crops
> based on soil and environmental conditions.

**⚠️ Disclaimer:** This system provides recommendations based on patterns learned
from training data. It does not guarantee crop success. Always consult local
agricultural experts before making farming decisions.

---

## 📋 Project Overview

This project is the **Phase 1** of the Smart Agriculture System, focused on
**Crop Recommendation**. The system accepts soil parameters (N, P, K, pH) and
environmental conditions (temperature, humidity, rainfall) to predict the most
suitable crops using a Random Forest Classifier.

### Current Features
- REST API for crop recommendation (top 3 predictions with model scores)
- Machine Learning pipeline (preprocessing, training, evaluation)
- Crop information database
- Recommendation history tracking
- Swagger/OpenAPI documentation

### Future Scope
- 🌿 Plant Disease Detection (Phase 2) — using MobileNetV2/EfficientNet
- 📱 Android Application — Kotlin + Jetpack Compose
- 👤 User Authentication & Profiles
- 📊 Advanced Analytics Dashboard

---

## 🛠️ Technology Stack

| Layer         | Technology                              |
|---------------|----------------------------------------|
| Backend       | Django 4.2, Django REST Framework      |
| ML            | Scikit-learn, Pandas, NumPy            |
| Database      | SQLite (dev), PostgreSQL (production)  |
| API Docs      | drf-spectacular, Swagger UI            |
| Testing       | pytest, Django TestCase                |

---

## 🏗️ System Architecture

```
Android App (future)
       │
       ▼
Django REST API  ──►  /api/v1/crops/recommend/
       │
       ▼
Prediction Service  ──►  Loads trained ML model
       │
       ▼
Random Forest Model  ──►  Returns top 3 crop recommendations
       │
       ▼
Crop Database  ──►  Stores crop info & recommendation history
```

---

## 📁 Project Structure

```
crop-recomend/
├── backend/              # Django project
│   ├── config/           # Django settings, URLs, WSGI/ASGI
│   ├── crop_recommendation/  # Main Django app
│   │   ├── services/     # Business logic (predictor)
│   │   ├── tests/        # Unit & API tests
│   │   └── migrations/
│   └── manage.py
│
├── ml/                   # Machine Learning pipeline
│   ├── preprocessing/    # Data validation & cleaning
│   ├── training/         # Model training & comparison
│   ├── evaluation/       # Metrics, confusion matrix
│   ├── inference/        # Standalone prediction
│   ├── artifacts/        # Saved models & metadata
│   └── config.py         # ML constants (feature order, random seed)
│
├── data/raw/             # Raw datasets
├── docs/                 # Documentation
├── requirements.txt
└── .env.example
```

---

## 🚀 Quick Start

> Detailed instructions in [docs/SETUP.md](docs/SETUP.md)

```bash
# 1. Clone the repository
git clone <repository-url>
cd crop-recomend

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env       # Windows
# cp .env.example .env       # macOS/Linux
# Edit .env and set your SECRET_KEY

# 5. Run migrations
cd backend
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Train the ML model (after placing dataset)
cd ..
python ml/training/train.py

# 8. Start the server
cd backend
python manage.py runserver
```

---

## 🔌 API Endpoints

| Method | Endpoint                   | Description              |
|--------|----------------------------|--------------------------|
| POST   | `/api/v1/crops/recommend/` | Get crop recommendations |
| GET    | `/api/v1/crops/`           | List all crops           |
| GET    | `/api/v1/crops/{id}/`      | Get crop details         |
| GET    | `/api/docs/`               | Swagger UI               |
| GET    | `/api/schema/`             | OpenAPI schema           |

### Example Request

```bash
curl -X POST http://127.0.0.1:8000/api/v1/crops/recommend/ \
  -H "Content-Type: application/json" \
  -d '{
    "nitrogen": 90,
    "phosphorus": 42,
    "potassium": 43,
    "temperature": 25.5,
    "humidity": 80.0,
    "ph": 6.5,
    "rainfall": 200.0
  }'
```

### Example Response

```json
{
    "success": true,
    "recommendations": [
        {"crop": "Rice", "score": 0.94},
        {"crop": "Maize", "score": 0.87},
        {"crop": "Cotton", "score": 0.72}
    ]
}
```

---

## 🧪 Testing

```bash
cd backend
python manage.py test
# or
pytest
```

---

## Dataset Preparation

The dataset is preprocessed using a reproducible pipeline:

```bash
# Run from the project root
python ml/preprocessing/preprocess.py
```

This command validates, analyzes, and cleans the raw dataset, generating:
- Processed dataset: `data/processed/crop_recommendation_clean.csv`
- Summary JSON: `data/processed/dataset_summary.json`
- Quality report: `docs/DATA_QUALITY_REPORT.md`
- Analysis plots: `ml/analysis/plots/`

For details see:
- [Dataset Information](docs/DATASET.md)
- [Data Quality Report](docs/DATA_QUALITY_REPORT.md)

---

## Documentation

- [Setup Guide](docs/SETUP.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Dataset Information](docs/DATASET.md)
- [Data Quality Report](docs/DATA_QUALITY_REPORT.md)
- [ML Model Details](docs/ML_MODEL.md)
- [API Reference](docs/API.md)

---

## 📄 License

This project is developed as a college industrial-training project.

---

*Built with ❤️ using Django, Scikit-learn, and Python*
