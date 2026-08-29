# ⚙️ Setup Guide

This guide provides step-by-step instructions to set up the Smart Agriculture
System (Crop Recommendation + Plant Disease Detection) on a development machine.

## Prerequisites

- Python 3.10 or later (3.12 recommended) — [python.org](https://www.python.org/downloads/)
- pip (included with Python)
- Git — [git-scm.com](https://git-scm.com/downloads)

Verify your Python installation:

```bash
python --version
pip --version
```

## 1. Clone the Repository

```bash
git clone <repository-url>
cd crop-recomend
```

## 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the virtual environment:

```bash
# Windows (Command Prompt)
venv\Scripts\activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# macOS / Linux / WSL
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** TensorFlow will be installed as part of the dependencies. It is required for the disease detection module. If you encounter issues on Windows, consider using WSL2 with Ubuntu for full GPU support.

## 4. Configure Environment Variables

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Edit `.env` and set a secret key:

```bash
# Generate a secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and paste it as the `SECRET_KEY` value in `.env`.

## 5. Run Database Migrations

```bash
cd backend
python manage.py migrate
```

## 6. Create a Superuser (Admin) — Optional

```bash
python manage.py createsuperuser
```

Follow the prompts to set username, email, and password.

## 7. Seed Crop Data — Optional

If the database is empty:

```bash
python manage.py seed_crops
```

## 8. Start the Development Server

```bash
python manage.py runserver
```

The server will start at: `http://127.0.0.1:8000/`

- Admin panel: `http://127.0.0.1:8000/admin/`
- API docs (Swagger): `http://127.0.0.1:8000/api/docs/`
- Crop recommendation: `POST http://127.0.0.1:8000/api/v1/crops/recommend/`
- Disease detection: `POST http://127.0.0.1:8000/api/v1/crops/disease/predict/`

## Important Notes on ML Models

### Disease Detection Model

The trained disease detection model (`ml/disease/artifacts/plant_disease_model.keras`) is **already included** in the repository. You do **not** need to retrain the model to use the API.

The model is loaded automatically when the disease prediction endpoint is first called.

### Crop Recommendation Model

The crop recommendation model (`ml/artifacts/crop_recommendation_model.joblib`) should also be present. If not, run the training script:

```bash
# From the project root (crop-recomend/)
python ml/training/train.py
```

### Retraining the Disease Model (Optional)

If you want to retrain the disease model from scratch:

1. Download the PlantVillage dataset.
2. Run the dataset preparation script:
   ```bash
   python scripts/prepare_disease_dataset.py
   ```
3. Run the training script (GPU recommended):
   ```bash
   python -m ml.disease.training.train_mobilenet
   ```

> **Note:** Retraining requires the full PlantVillage dataset (~54,000 images) and is best performed in a GPU-accelerated environment (e.g., WSL2 + Ubuntu with NVIDIA CUDA).

## 9. Run Tests

```bash
cd backend
python manage.py test
```

Or with pytest:

```bash
cd backend
pytest
```

## WSL2 Setup (for GPU-Accelerated Training/Inference)

The disease model was trained on WSL2 + Ubuntu with TensorFlow GPU support. To replicate:

1. Install WSL2 with Ubuntu.
2. Install NVIDIA drivers and CUDA toolkit.
3. Create a Python virtual environment in WSL:
   ```bash
   python3 -m venv ~/crop-disease-venv
   source ~/crop-disease-venv/bin/activate
   ```
4. Install requirements:
   ```bash
   pip install -r /mnt/d/Projects/Django\ backend/crop-recomend/requirements.txt
   ```
5. Run the server:
   ```bash
   cd "/mnt/d/Projects/Django backend/crop-recomend/backend"
   python manage.py runserver
   ```

## Troubleshooting

### "ModuleNotFoundError: No module named 'django'"
Make sure your virtual environment is activated (`venv\Scripts\activate`).

### "Error: That port is already in use."
Use a different port: `python manage.py runserver 8001`

### PowerShell execution policy error
Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### TensorFlow import errors
If TensorFlow fails to import, ensure you have a compatible Python version (3.10–3.12). On Windows, WSL2 is recommended for GPU support.
