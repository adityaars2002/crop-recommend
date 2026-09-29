"""
Django settings for Smart Agriculture System.

This is the main configuration file for the Django project.
It uses python-dotenv to load environment variables from a .env file.

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# ==============================================================================
# PATHS
# ==============================================================================

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR points to the 'backend/' directory.
BASE_DIR = Path(__file__).resolve().parent.parent

# PROJECT_ROOT points to the top-level 'crop-recomend/' directory.
PROJECT_ROOT = BASE_DIR.parent

# Load environment variables from .env file at project root
load_dotenv(PROJECT_ROOT / '.env')

# ==============================================================================
# CORE SETTINGS
# ==============================================================================

SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'django-insecure-dev-key-change-this-in-production'
)

DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost,10.0.2.2').split(',')
    if host.strip()
]

# Render sets RENDER_EXTERNAL_HOSTNAME automatically
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# CSRF trusted origins for production (needed when frontend POSTs to backend)
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')
    if origin.strip()
]

# ==============================================================================
# APPLICATION DEFINITION
# ==============================================================================

INSTALLED_APPS = [
    # Django built-in apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'corsheaders',
    'drf_spectacular',

    # Local apps
    'crop_recommendation',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Must be before CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ==============================================================================
# DATABASE
# ==============================================================================
# Uses DATABASE_URL if set (e.g., PostgreSQL on Render), otherwise falls
# back to SQLite for local development.

DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

# ==============================================================================
# PASSWORD VALIDATION
# ==============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==============================================================================
# INTERNATIONALIZATION
# ==============================================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ==============================================================================
# STATIC FILES
# ==============================================================================

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise — compressed and cached static files in production
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ==============================================================================
# DEFAULT PRIMARY KEY
# ==============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================================
# DJANGO REST FRAMEWORK
# ==============================================================================

REST_FRAMEWORK = {
    # Use JSON as the default renderer; enable Browsable API only in debug
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ] + (
        ['rest_framework.renderers.BrowsableAPIRenderer'] if DEBUG else []
    ),

    # Default parser classes
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],

    # Schema generation with drf-spectacular
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

    # No authentication required for now (will be added later)
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],

    # Exception handling
    'EXCEPTION_HANDLER': 'crop_recommendation.exceptions.custom_exception_handler',
}

# ==============================================================================
# DRF SPECTACULAR (OpenAPI / Swagger)
# ==============================================================================

SPECTACULAR_SETTINGS = {
    'TITLE': 'Smart Agriculture System API',
    'DESCRIPTION': (
        'REST API for the Smart Agriculture System.\n\n'
        'Provides two AI/ML capabilities:\n'
        '1. **Crop Recommendation** — predicts suitable crops based on soil and '
        'environmental parameters using a Random Forest model.\n'
        '2. **Plant Disease Detection** — classifies plant leaf images into 38 '
        'disease/health categories using a fine-tuned MobileNetV2 model.\n\n'
        '**Disclaimer:** Recommendations and predictions are based on patterns '
        'learned from training data and do not guarantee crop success or '
        'perfect diagnosis.'
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,

    # Group endpoints by tags
    'TAGS': [
        {
            'name': 'Crops',
            'description': 'Crop information and recommendation endpoints',
        },
        {
            'name': 'Disease Detection',
            'description': 'Plant disease prediction from leaf images',
        },
    ],
}

# ==============================================================================
# CORS CONFIGURATION
# ==============================================================================
# For development, allow all origins. In production, configure specific origins.

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = [
        origin.strip()
        for origin in os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
        if origin.strip()
    ]

CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'OPTIONS',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'origin',
    'user-agent',
]

# ==============================================================================
# ML MODEL CONFIGURATION
# ==============================================================================
# Path to the ML artifacts directory (relative to PROJECT_ROOT)

ML_ARTIFACTS_DIR = PROJECT_ROOT / 'ml' / 'artifacts'
ML_MODEL_PATH = ML_ARTIFACTS_DIR / 'crop_recommendation_model.joblib'
ML_METADATA_PATH = ML_ARTIFACTS_DIR / 'feature_metadata.json'

# ==============================================================================
# LOGGING
# ==============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'crop_recommendation': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True,
        },
    },
}
