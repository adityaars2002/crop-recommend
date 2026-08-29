# 🌾 Smart Agriculture System — Crop Recommendation and Plant Disease Detection

> An AI/ML-powered decision-support system that provides crop recommendations based on environmental conditions and detects plant diseases from leaf images.

**⚠️ Disclaimer:** This system provides recommendations and predictions based on patterns learned from training data. It does not guarantee crop success or perfect disease diagnosis. Always consult local agricultural experts before making farming decisions.

---

## 📋 Overview

This project provides a comprehensive agricultural assistance platform, integrating two major machine learning capabilities through a Django REST Framework backend:

1. **Crop Recommendation:** Recommends the most suitable crops based on soil nutrients (N, P, K), pH, temperature, humidity, and rainfall.
2. **Plant Disease Detection:** Analyzes images of plant leaves to detect 38 different categories of crop diseases and healthy states.

These two capabilities complement each other by assisting farmers in both the planning phase (choosing the right crop) and the maintenance phase (identifying and treating diseases).

---

## ✨ Key Features

- **Crop Recommendation:**
  - Machine learning based on 7 environmental/soil parameters.
  - Outputs top 3 crop recommendations with confidence scores.
- **Plant Disease Detection:**
  - 38-class plant disease classification.
  - Detects both healthy and diseased states across multiple crops.
  - Returns top-3 disease predictions with confidence scores.
  - Powered by a fine-tuned MobileNetV2 transfer learning model.
  - Accepts multipart image uploads via the API.
- **Django REST Framework API:**
  - Unified backend serving both ML models.
  - Swagger/OpenAPI documentation (via `drf-spectacular`).
- **Comprehensive ML Pipelines:**
  - GPU-accelerated training scripts.
  - Model evaluation with confusion matrices and per-class metrics.
  - Misclassification analysis.

---

## 🏗️ System Architecture

### 1. General Flow
```
User/Client Application
       │
       ▼
Django REST API
       │
       ├─────────────────────────────────┐
       ▼                                 ▼
Crop Recommendation              Disease Detection
(Tabular Data)                   (Image Upload)
       │                                 │
       ▼                                 ▼
ML Inference                     ML Inference
(Random Forest)                  (MobileNetV2)
       │                                 │
       ▼                                 ▼
JSON Response                    JSON Response
```

### 2. Disease Detection Flow
1. **Image Upload:** The client sends an image via `multipart/form-data` to the Django API.
2. **Temporary Handling:** Django securely saves the image to a temporary file.
3. **Preprocessing:** The image is resized to 224×224×3 and preprocessed for MobileNetV2.
4. **Model Inference:** The trained `.keras` model predicts the class probabilities across 38 classes.
5. **Post-processing:** The system retrieves the top prediction and top 3 candidates, formatting them into crop, disease, status, and score.
6. **JSON Response:** The backend returns the results to the client.

---

## 📁 Project Structure

```
crop-recomend/
├── backend/              # Django project and API
│   ├── config/           # Django settings and routing
│   └── crop_recommendation/ # Django app (serializers, views, models)
├── data/                 # Raw tabular datasets (images ignored in Git)
├── docs/                 # Detailed documentation files
├── ml/                   # Machine Learning pipelines
│   ├── preprocessing/    # Crop recommendation ML
│   ├── training/         # Crop recommendation ML
│   └── disease/          # Plant Disease ML Module
│       ├── analysis/     # Data distribution and analysis scripts
│       ├── artifacts/    # Trained models (.keras files)
│       ├── data/         # PlantVillage dataset handling
│       ├── evaluation/   # Evaluation metrics, confusion matrix, and JSON reports
│       ├── inference/    # Standalone prediction script
│       ├── metadata/     # Class mappings and weights
│       └── training/     # Model training and fine-tuning scripts
├── scripts/              # Helper scripts (e.g., CLI prediction)
└── requirements.txt      # Python dependencies
```

---

## 🌾 Crop Recommendation Model

- **Input Features:** 7 (Nitrogen, Phosphorus, Potassium, Temperature, Humidity, pH, Rainfall)
- **Model / Algorithm:** Random Forest Classifier
- **Output Classes:** 22 unique crop categories
- **API Endpoint:** `POST /api/v1/crops/recommend/`
- **Response:** JSON list of the top 3 recommended crops with probability scores.

---

## 🌿 Plant Disease Detection Model

The disease detection module is built using transfer learning on the PlantVillage dataset.

- **Model Architecture:** MobileNetV2 (pretrained on ImageNet)
- **Input Image Size:** 224 × 224 × 3
- **Number of Classes:** 38
- **Batch Size:** 16 (during final training)
- **Mixed Precision:** Enabled (`mixed_float16`)
- **Final Layer:** Float32 output for numerical stability

### Training Strategy
The model was trained in three stages:
1. **Stage 1 (Baseline):** MobileNetV2 backbone frozen; only the top classification head was trained.
2. **Stage 2 (Class-Weighted):** Same as baseline, but with class weights applied to handle dataset imbalances.
3. **Stage 3 (Fine-Tuning):** The last 30 layers of MobileNetV2 were unfrozen. **BatchNormalization layers were kept frozen** to prevent destroying the learned statistics.

The final model was selected based on validation performance during Stage 3.

---

## 📊 Dataset (PlantVillage)

The disease detection model was trained on the PlantVillage dataset, which includes images of crops in both healthy and diseased states.

- **Total Classes:** 38 (combinations of crops and specific diseases or healthy states)
- **Dataset Split:** 70% Train, 15% Validation, 15% Test
- **Total Test Images:** 8,176

**⚠️ Important:** The raw PlantVillage dataset is intentionally NOT committed to GitHub due to its size. To retrain the model, you must download the dataset separately and prepare it using the provided scripts.

---

## 📈 Training Results & Model Comparison

The final evaluation was performed on the unseen Test Set.

| Metric | Value |
|--------|-------|
| Test Accuracy | 0.9705 (97.05%) |
| Macro F1 Score | 0.9657 |
| Weighted F1 Score | 0.9706 |
| Total Parameters | 2,306,662 |
| Trainable Parameters| 1,559,398 |
| Model Size | ~33.2 MB |

### Model Comparison (Validation Metrics)

| Experiment | Backbone | Validation Accuracy | Validation Loss | Notes |
|------------|----------|---------------------|-----------------|-------|
| `exp_baseline` | MobileNetV2 | 0.9515 | 0.1542 | Stage 1 (Frozen Backbone) |
| `exp_class_weight` | MobileNetV2 | 0.9493 | 0.1568 | Stage 2 (Class Weights) |
| `exp_finetuned` | MobileNetV2 | **0.9717** | **0.0834** | Stage 3 (Last 30 layers un-frozen) |

*The `exp_finetuned` model was selected as the final production model (`plant_disease_model.keras`).*

---

## 🔌 API Documentation

### 1. Disease Detection
- **Endpoint:** `POST /api/v1/crops/disease/predict/`
- **Content-Type:** `multipart/form-data`
- **Request Field:** `image` (File upload)

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
            "score": 0.9982
        },
        "top_3": [
            {
                "class_name": "Tomato___Late_blight",
                "crop": "Tomato",
                "disease": "Late blight",
                "status": "diseased",
                "score": 0.9982
            },
            ...
        ]
    }
}
```

### 2. Crop Recommendation
- **Endpoint:** `POST /api/v1/crops/recommend/`
- **Content-Type:** `application/json`

*Refer to [docs/API.md](docs/API.md) for full API details.*

---

## 🚀 Running the Project

### Setup Guide
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd crop-recomend
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   # source venv/bin/activate   # macOS/Linux
   ```
3. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure environment variables:**
   ```bash
   copy .env.example .env       # Windows
   # cp .env.example .env       # macOS/Linux
   # Edit .env and set your SECRET_KEY
   ```
5. **Run Django migrations:**
   ```bash
   cd backend
   python manage.py migrate
   ```
6. **Start the Django server:**
   ```bash
   python manage.py runserver
   ```

**Note on ML Models:** The trained final model for disease detection (`plant_disease_model.keras`) is already included in the repository. **You do not need to retrain the model to use the API.** 

---

## 💻 Command-Line Disease Prediction Example

You can run disease prediction directly from the command line using the provided script without starting the server:

```bash
# Run from the project root
python scripts/predict_disease.py "path/to/your/leaf_image.jpg"
```

---

## 📄 Documentation Links
- [API Reference](docs/API.md)
- [Architecture](docs/ARCHITECTURE.md)
- [ML Model Details](docs/ML_MODEL.md)
- [Setup Guide](docs/SETUP.md)

---

*Built with ❤️ using Django, Scikit-learn, TensorFlow, and Python*
