# 🌾 Smart Agriculture System — Crop Recommendation and Plant Disease Detection

> An AI/ML-powered decision-support system that recommends suitable crops based on environmental conditions and detects plant diseases from leaf images.

**⚠️ Disclaimer:** This system provides recommendations and predictions based on patterns learned from training data. It does not guarantee crop success or perfect disease diagnosis. Always consult local agricultural experts before making farming decisions.

---

## 📋 Overview

This project provides a comprehensive agricultural assistance platform, integrating two major machine learning capabilities through a Django REST Framework backend:

1. **Crop Recommendation:** Uses 7 soil and environmental parameters (Nitrogen, Phosphorus, Potassium, Temperature, Humidity, pH, Rainfall) to recommend the most suitable crops for cultivation using a Random Forest Classifier.

2. **Plant Disease Detection:** Accepts a photograph of a plant leaf and classifies it into one of 38 categories (covering multiple crops and their diseases, as well as healthy states) using a fine-tuned MobileNetV2 deep learning model.

These two capabilities complement each other by assisting farmers in both the **planning phase** (choosing the right crop) and the **maintenance phase** (identifying and treating diseases early).

---

## ✨ Key Features

### Crop Recommendation
- Soil and environmental parameter-based prediction (7 inputs)
- Random Forest classifier trained on 22 crop classes
- Top-3 crop recommendations with probability scores
- Recommendation history tracking

### Plant Disease Detection
- 38-class plant disease/health classification
- Covers 14 crop species
- Identifies both healthy and diseased states
- MobileNetV2 transfer learning with fine-tuning
- Top-3 predictions with confidence scores
- Returns crop name, disease name, health status, and score
- Multipart image upload via REST API

### Backend / API
- Django REST Framework API serving both ML models
- Swagger/OpenAPI documentation via `drf-spectacular`
- Consistent JSON response envelopes
- Input validation and error handling
- Paginated crop listing and recommendation history

---

## 🛠️ Technology Stack

### Backend
| Technology | Purpose |
|---|---|
| Python 3.12 | Core language |
| Django 4.2 | Web framework |
| Django REST Framework | REST API |
| drf-spectacular | OpenAPI / Swagger docs |
| python-dotenv | Environment configuration |

### Machine Learning
| Technology | Purpose |
|---|---|
| Scikit-learn | Crop recommendation (Random Forest) |
| TensorFlow / Keras | Disease detection (MobileNetV2) |
| MobileNetV2 | Pretrained CNN backbone (ImageNet) |

### Data & Image Processing
| Technology | Purpose |
|---|---|
| NumPy | Numerical computation |
| Pandas | Data analysis |
| Pillow (PIL) | Image loading and processing |

### Visualization / Evaluation
| Technology | Purpose |
|---|---|
| Matplotlib | Training plots, confusion matrix |
| Seaborn | Data distribution visualizations |
| Scikit-learn metrics | Classification reports, F1 scores |

### Development Environment
| Technology | Purpose |
|---|---|
| Git | Version control |
| SQLite | Development database |
| WSL2 + Ubuntu | TensorFlow GPU training environment |
| NVIDIA CUDA / cuDNN | GPU acceleration for model training |

---

## 🏗️ System Architecture

### General Flow

```
User / Client (Postman, curl, future Android app)
      │
      ▼
Django REST Framework API
      │
      ├──────────────────────────────────┐
      │                                  │
      ▼                                  ▼
Crop Recommendation               Disease Detection
(JSON input)                      (Image upload)
      │                                  │
      ▼                                  ▼
Random Forest Model               MobileNetV2 Model
      │                                  │
      ▼                                  ▼
Crop probabilities                38-class probabilities
      │                                  │
      └────────────┬─────────────────────┘
                   │
                   ▼
           JSON Response
```

### Disease Detection Pipeline

```
Image Upload (multipart/form-data)
    → Django API receives file
    → Saved to temporary file
    → Image resized to 224 × 224 × 3
    → MobileNetV2 preprocess_input (scale to [-1, 1])
    → Trained .keras model inference
    → 38-class softmax prediction
    → Top prediction + Top 3 extracted
    → Each prediction mapped to: crop / disease / status / score
    → Temporary file cleaned up
    → JSON response returned
```

---

## 📁 Project Structure

```
crop-recomend/
├── backend/                        # Django project
│   ├── config/                     # Django settings, root URLs, WSGI/ASGI
│   ├── crop_recommendation/        # Main Django app
│   │   ├── services/               # Business logic (crop predictor)
│   │   ├── views.py                # API views (recommendation + disease)
│   │   ├── serializers.py          # Input validation
│   │   ├── models.py               # Crop, Recommendation models
│   │   ├── urls.py                 # App URL routing
│   │   └── tests/                  # Unit & API tests
│   ├── db.sqlite3                  # Development database
│   └── manage.py
│
├── ml/                             # Machine Learning pipelines
│   ├── config.py                   # Crop recommendation ML config
│   ├── preprocessing/              # Crop data validation & cleaning
│   ├── training/                   # Crop model training & comparison
│   ├── evaluation/                 # Crop model metrics
│   ├── inference/                  # Crop standalone prediction
│   ├── artifacts/                  # Crop model artifacts (.joblib)
│   └── disease/                    # Plant Disease Detection module
│       ├── training/               # Training scripts & config
│       │   ├── config.py           # Hyperparameters (image size, batch, LR)
│       │   └── train_mobilenet.py  # 3-stage training pipeline
│       ├── inference/              # Disease inference
│       │   └── predictor.py        # Load model, predict, format results
│       ├── evaluation/             # Evaluation results
│       │   ├── experiments.csv     # Experiment comparison
│       │   ├── classification_report.txt
│       │   ├── model_info.json     # Parameter counts, F1 scores
│       │   └── plots/              # Confusion matrix, training curves
│       ├── artifacts/              # Trained models
│       │   └── plant_disease_model.keras  # Final production model
│       ├── metadata/               # Class mappings
│       │   ├── class_mapping.json  # Index → crop/disease/status
│       │   ├── class_names.json    # Ordered class name list
│       │   └── class_weights.json  # Class weights for imbalanced training
│       ├── analysis/               # Dataset EDA plots
│       └── data/                   # Dataset loading utilities
│
├── data/                           # Datasets (tabular; images excluded from Git)
├── docs/                           # Documentation
├── scripts/                        # Helper scripts
│   ├── predict_disease.py          # CLI disease prediction
│   ├── prepare_disease_dataset.py  # Dataset preparation & EDA
│   └── generate_report.py         # Report generation
│
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## 🌾 Crop Recommendation Model

| Property | Value |
|---|---|
| **Algorithm** | Random Forest Classifier |
| **Library** | scikit-learn |
| **Input Features** | 7 — Nitrogen (N), Phosphorus (P), Potassium (K), Temperature, Humidity, pH, Rainfall |
| **Output** | 22 crop classes |
| **Prediction** | Top 3 crops with probability scores |
| **API Endpoint** | `POST /api/v1/crops/recommend/` |
| **Test Accuracy** | 99.55% |

For full model details, see [docs/ML_MODEL_REPORT.md](docs/ML_MODEL_REPORT.md).

---

## 🌿 Plant Disease Detection Model

### Architecture

| Property | Value |
|---|---|
| **Base Model** | MobileNetV2 (pretrained on ImageNet) |
| **Input Size** | 224 × 224 × 3 (RGB) |
| **Number of Classes** | 38 |
| **Classification Head** | GlobalAveragePooling2D → Dropout(0.2) → Dense(38, softmax) |
| **Final Layer Dtype** | float32 (for numerical stability with mixed precision) |
| **Batch Size** | 16 |
| **Mixed Precision** | Enabled (`mixed_float16`) |

### Why MobileNetV2?

- **Lightweight architecture** — efficient for both training and inference
- **Strong transfer learning baseline** — ImageNet weights provide rich feature representations
- **Reduced training requirements** — only the classification head and top layers need training
- **Suitable for eventual mobile deployment** — can be converted to TFLite for on-device inference

### Data Augmentation

Applied only to the training set to improve generalization:

- `RandomFlip` (horizontal)
- `RandomRotation` (10%)
- `RandomZoom` (10%)
- `RandomTranslation` (10% horizontal and vertical)
- `RandomContrast` (10%)

### Three-Stage Training Pipeline

| Stage | Description | Backbone | Learning Rate | Epochs |
|---|---|---|---|---|
| **1. Baseline** | Train classification head only | Frozen | 1e-3 | 15 |
| **2. Class-Weighted** | Apply class weights for imbalanced classes | Frozen | 1e-3 | 15 |
| **3. Fine-Tuning** | Unfreeze last 30 layers, keep BatchNorm frozen | Partially unfrozen | 1e-5 | 10 |

**Key detail:** During fine-tuning (Stage 3), all `BatchNormalization` layers remain frozen to prevent destroying the running mean/variance statistics learned from ImageNet.

The experiments were compared using validation metrics, and the **fine-tuned model** was selected as the final model based on the best validation accuracy.

---

## 📊 Dataset (PlantVillage)

The disease detection model was trained on the **PlantVillage** dataset.

| Property | Value |
|---|---|
| **Total Images** | ~54,305 |
| **Total Classes** | 38 |
| **Crop Species** | 14 (Apple, Blueberry, Cherry, Corn, Grape, Orange, Peach, Pepper, Potato, Raspberry, Soybean, Squash, Strawberry, Tomato) |
| **Split** | 70% Train / 15% Validation / 15% Test |
| **Test Set Size** | 8,176 images |
| **Random Seed** | 42 |

### ⚠️ Dataset Not Included in Repository

The raw PlantVillage dataset is **intentionally NOT committed** to GitHub because of its large size (~2 GB).

The dataset is required **only for:**
- Re-running the dataset preparation script
- Retraining the model from scratch
- Reproducing the full evaluation pipeline

The dataset is **NOT required for:**
- Running the Django API server
- Making disease predictions (the trained model is already included)
- Running the CLI prediction script

To prepare the dataset for retraining, see `scripts/prepare_disease_dataset.py`.

For dataset details, see [docs/DISEASE_DATASET.md](docs/DISEASE_DATASET.md).

---

## 📈 Training Results

### Final Test Set Metrics (Disease Detection)

| Metric | Value |
|---|---|
| **Test Accuracy** | 0.9705 (97.05%) |
| **Macro F1 Score** | 0.9657 |
| **Weighted F1 Score** | 0.9706 |
| **Total Parameters** | 2,306,662 |
| **Trainable Parameters** | 1,559,398 |
| **Non-trainable Parameters** | 747,264 |
| **Model File Size** | ~33.2 MB |

### Model Comparison (Validation Metrics)

| Experiment | Validation Accuracy | Validation Loss | Notes |
|---|---|---|---|
| `exp_baseline` | 0.9515 | 0.1542 | Stage 1 — Frozen backbone |
| `exp_class_weight` | 0.9493 | 0.1568 | Stage 2 — Class weights applied |
| `exp_finetuned` | **0.9717** | **0.0834** | Stage 3 — Last 30 layers unfrozen |

> **Note:** The validation metrics above were used for model selection. The test metrics in the table above are from a **separate, held-out test set** that was never seen during training or model selection.

The `exp_finetuned` model was selected as the final production model and saved as:
`ml/disease/artifacts/plant_disease_model.keras`

For per-class metrics, see `ml/disease/evaluation/classification_report.txt`.

---

## 🔌 API Documentation

### 1. Crop Recommendation

- **Endpoint:** `POST /api/v1/crops/recommend/`
- **Content-Type:** `application/json`

**Request Body (all fields required):**

| Field | Type | Description | Constraints |
|---|---|---|---|
| `nitrogen` | float | Soil Nitrogen (N) | ≥ 0 |
| `phosphorus` | float | Soil Phosphorus (P) | ≥ 0 |
| `potassium` | float | Soil Potassium (K) | ≥ 0 |
| `temperature` | float | Average Temperature (°C) | — |
| `humidity` | float | Relative Humidity (%) | 0–100 |
| `ph` | float | Soil pH value | 0–14 |
| `rainfall` | float | Rainfall (mm) | ≥ 0 |

**Example Request:**
```json
{
    "nitrogen": 90,
    "phosphorus": 42,
    "potassium": 43,
    "temperature": 25.5,
    "humidity": 80.0,
    "ph": 6.5,
    "rainfall": 200.0
}
```

**Example Response:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "created_at": "2026-08-25T16:50:30.868484+05:30",
        "input": {
            "nitrogen": 90.0,
            "phosphorus": 42.0,
            "potassium": 43.0,
            "temperature": 25.5,
            "humidity": 80.0,
            "ph": 6.5,
            "rainfall": 200.0
        },
        "recommendations": [
            {"rank": 1, "crop": {"id": 21, "name": "rice", ...}, "score": 0.504},
            {"rank": 2, "crop": {"id": 9, "name": "jute", ...}, "score": 0.482},
            {"rank": 3, "crop": {"id": 18, "name": "papaya", ...}, "score": 0.014}
        ]
    }
}
```

---

### 2. Disease Detection

- **Endpoint:** `POST /api/v1/crops/disease/predict/`
- **Content-Type:** `multipart/form-data`
- **Request Field:** `image` (file upload — JPEG, PNG, etc.)

**Example Response:**
```json
{
    "success": true,
    "data": {
        "prediction": {
            "class_name": "Tomato___Late_blight",
            "crop": "Tomato",
            "disease": "Late blight",
            "status": "diseased",
            "score": 0.9878
        },
        "top_3": [
            {
                "class_name": "Tomato___Late_blight",
                "crop": "Tomato",
                "disease": "Late blight",
                "status": "diseased",
                "score": 0.9878
            },
            {
                "class_name": "Tomato___Early_blight",
                "crop": "Tomato",
                "disease": "Early blight",
                "status": "diseased",
                "score": 0.0089
            },
            {
                "class_name": "Tomato___healthy",
                "crop": "Tomato",
                "disease": "healthy",
                "status": "healthy",
                "score": 0.0021
            }
        ]
    }
}
```

**Response Field Descriptions:**

| Field | Description |
|---|---|
| `class_name` | The raw PlantVillage class label (e.g., `Tomato___Late_blight`) |
| `crop` | The identified crop species (e.g., `Tomato`) |
| `disease` | The specific disease name, or `healthy` if no disease detected |
| `status` | Either `healthy`, `diseased`, or `uncertain` (if score < 0.5) |
| `score` | The model's softmax probability (0.0–1.0). Example: 0.9878 ≈ 98.78% confidence. **This is the model's statistical confidence, not a guaranteed diagnosis.** |

---

### 3. Other Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/crops/` | List all supported crops (paginated) |
| `GET` | `/api/v1/crops/{id}/` | Get crop details |
| `GET` | `/api/v1/crops/recommendations/history/` | Past recommendation history |
| `GET` | `/api/docs/` | Swagger UI |
| `GET` | `/api/schema/` | OpenAPI schema |

For complete API documentation, see [docs/API.md](docs/API.md).

---

## 🧪 Testing APIs with Postman

### Disease Detection

1. Start the Django server (`python manage.py runserver`).
2. Open Postman and create a new **POST** request.
3. Set URL to: `http://127.0.0.1:8000/api/v1/crops/disease/predict/`
4. Under **Body**, select **form-data**.
5. Add a key named `image`, change its type to **File**.
6. Select a plant leaf image from your computer.
7. Click **Send**.
8. You should receive a JSON response with `prediction` and `top_3` fields.

### Crop Recommendation

1. Create a new **POST** request in Postman.
2. Set URL to: `http://127.0.0.1:8000/api/v1/crops/recommend/`
3. Under **Body**, select **raw** and change the type to **JSON**.
4. Paste the following:
```json
{
    "nitrogen": 90,
    "phosphorus": 42,
    "potassium": 43,
    "temperature": 25.5,
    "humidity": 80.0,
    "ph": 6.5,
    "rainfall": 200.0
}
```
5. Click **Send**.
6. You should receive a JSON response with top 3 crop recommendations.

---

## 🚀 Running the Project

### Prerequisites

- Python 3.10+ (Python 3.12 recommended)
- pip
- Git

### Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd crop-recomend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv

   # Windows (Command Prompt)
   venv\Scripts\activate

   # Windows (PowerShell)
   venv\Scripts\Activate.ps1

   # macOS / Linux / WSL
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   # Windows
   copy .env.example .env

   # macOS / Linux / WSL
   cp .env.example .env
   ```
   Edit `.env` and set your `SECRET_KEY`.

5. **Run Django migrations:**
   ```bash
   cd backend
   python manage.py migrate
   ```

6. **Start the Django server:**
   ```bash
   python manage.py runserver
   ```

7. **Access the API:**
   - API Base: `http://127.0.0.1:8000/api/v1/crops/`
   - Swagger Docs: `http://127.0.0.1:8000/api/docs/`

> **Important:** The trained disease model (`plant_disease_model.keras`) is already included in the repository. **You do not need to retrain the model to use the API.** The model is loaded automatically when the disease prediction endpoint is called.

### WSL2 Environment (for GPU-accelerated training/inference)

The disease detection model was trained using TensorFlow with GPU support on WSL2 + Ubuntu. If you want to use the same environment:

```bash
# From WSL2/Ubuntu terminal
source ~/crop-disease-venv/bin/activate
cd "/mnt/d/Projects/Django backend/crop-recomend/backend"
python manage.py runserver
```

The project repository is stored on the Windows filesystem and accessed from WSL via `/mnt/d/...`.

---

## ⚡ GPU / CPU Support

- **GPU acceleration** was used during model training via TensorFlow with NVIDIA CUDA/cuDNN on WSL2.
- An **NVIDIA GPU is NOT required** to run the API server or make predictions. TensorFlow will fall back to CPU inference automatically.
- **CPU inference** is functional but slower than GPU inference.
- The PlantVillage dataset is required **only for retraining**, not for ordinary inference.
- Mixed precision (`mixed_float16`) is used during training to reduce GPU memory usage. It does not affect CPU inference.

---

## 💻 Command-Line Disease Prediction

You can run disease prediction directly from the command line without starting the Django server:

```bash
# Run from the project root
python scripts/predict_disease.py "path/to/your/leaf_image.jpg"
```

The script loads the trained model, processes the image, and prints:
- Crop name
- Disease name
- Health status
- Prediction score
- Top 3 predictions

> **Note:** The image path must point to an actual image file on your local filesystem.

---

## 📄 Documentation

| Document | Description |
|---|---|
| [API Reference](docs/API.md) | Full API endpoint documentation |
| [Architecture](docs/ARCHITECTURE.md) | System architecture and design |
| [ML Model Details](docs/ML_MODEL.md) | Both ML models overview |
| [Crop Recommendation Report](docs/ML_MODEL_REPORT.md) | Detailed crop model report |
| [Disease Model Report](docs/DISEASE_MODEL_REPORT.md) | Disease model training report |
| [Disease Model Card](docs/DISEASE_MODEL_CARD.md) | Standardized model card |
| [Disease Dataset](docs/DISEASE_DATASET.md) | PlantVillage dataset details |
| [Crop Data](docs/CROP_DATA.md) | Crop database documentation |
| [Setup Guide](docs/SETUP.md) | Detailed setup instructions |

---

## 🚀 Deployment

This project is configured for deployment on [Render](https://render.com/) using the free tier.

### Architecture

| Component | Service Type | Technology |
|---|---|---|
| **Backend** | Render Web Service | Django + Gunicorn + WhiteNoise |
| **Frontend** | Render Static Site | React + Vite |
| **Database** | Render PostgreSQL | PostgreSQL (free tier) |

### Environment Variables

#### Backend (Render Web Service)

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | Yes | Django secret key (auto-generated by render.yaml) |
| `DEBUG` | Yes | Set to `False` for production |
| `ALLOWED_HOSTS` | Yes | `.onrender.com` or your custom domain |
| `DATABASE_URL` | Yes | PostgreSQL connection string (auto-set by Render) |
| `CORS_ALLOWED_ORIGINS` | Yes | Frontend URL, e.g. `https://smart-agriculture-frontend.onrender.com` |
| `CSRF_TRUSTED_ORIGINS` | Yes | Same as CORS origins |
| `PYTHON_VERSION` | Recommended | `3.11.10` |

#### Frontend (Render Static Site)

| Variable | Required | Description |
|---|---|---|
| `VITE_API_BASE_URL` | Yes | Backend URL, e.g. `https://smart-agriculture-api.onrender.com` |

### Deploy from GitHub

#### Option 1: Using render.yaml Blueprint

1. Push this repository to GitHub.
2. Go to [Render Dashboard](https://dashboard.render.com/) → **New** → **Blueprint**.
3. Connect your GitHub repository.
4. Render will detect `render.yaml` and create all services automatically.
5. After the first deploy, set the remaining environment variables:
   - **Backend**: Set `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` to the frontend's Render URL.
   - **Frontend**: Set `VITE_API_BASE_URL` to the backend's Render URL.
6. Redeploy the frontend after setting `VITE_API_BASE_URL` (Vite inlines env vars at build time).

#### Option 2: Manual Setup

**Backend:**
1. Go to Render → **New** → **Web Service**.
2. Connect your GitHub repo.
3. Set the root directory to `./` (project root).
4. Build command: `pip install -r requirements.txt && cd backend && python manage.py collectstatic --noinput && python manage.py migrate`
5. Start command: `cd backend && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
6. Add all required environment variables.

**Frontend:**
1. Go to Render → **New** → **Static Site**.
2. Connect your GitHub repo.
3. Set the root directory to `frontend`.
4. Build command: `npm install && npm run build`
5. Publish directory: `dist`
6. Set `VITE_API_BASE_URL` to the backend URL.

**Database:**
1. Go to Render → **New** → **PostgreSQL**.
2. Create a free-tier database.
3. Copy the Internal Database URL and set it as `DATABASE_URL` on the backend.

### Post-Deployment: Seed Crop Data

After the first deploy with a fresh PostgreSQL database, the Crop table will be empty. Run the seed command using Render's shell:

```bash
cd backend && python manage.py seed_crops
```

### ⚠️ Free Tier Limitations

- **Cold starts:** Render free web services spin down after 15 minutes of inactivity. The first request after inactivity may take 30–60 seconds while the service starts up. TensorFlow model loading adds additional startup time.
- **Ephemeral filesystem:** Uploaded images are processed in-memory/temp files and cleaned up immediately (already handled). SQLite is **not** used in production — PostgreSQL is configured via `DATABASE_URL`.
- **Memory:** The free tier has 512 MB RAM. TensorFlow + the Keras model (~33 MB) should fit, but monitor memory usage.
- **This is not a production-grade deployment.** It is suitable for demos, portfolios, and development purposes.

---

## 📄 License

This project is developed as a college industrial-training project.

---

*Built with ❤️ using Django, Scikit-learn, TensorFlow, and Python*

