# ⚙️ Setup Guide

This guide provides step-by-step instructions to set up the Smart Agriculture
System on a **Windows** development machine.

## Prerequisites

- Python 3.10 or later ([python.org](https://www.python.org/downloads/))
- pip (included with Python)
- Git ([git-scm.com](https://git-scm.com/downloads))

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

# macOS / Linux
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

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

## 6. Create a Superuser (Admin)

```bash
python manage.py createsuperuser
```

Follow the prompts to set username, email, and password.

## 7. Start the Development Server

```bash
python manage.py runserver
```

The server will start at: `http://127.0.0.1:8000/`

- Admin panel: `http://127.0.0.1:8000/admin/`
- API docs: `http://127.0.0.1:8000/api/docs/`

## 8. Train the ML Model (After Phase 3)

> This step requires the dataset to be placed in `data/raw/`.

```bash
# From the project root (crop-recomend/)
python ml/training/train.py
```

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

## Troubleshooting

### "ModuleNotFoundError: No module named 'django'"
Make sure your virtual environment is activated (`venv\Scripts\activate`).

### "Error: That port is already in use."
Use a different port: `python manage.py runserver 8001`

### PowerShell execution policy error
Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
