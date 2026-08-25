"""
App configuration for the Crop Recommendation module.

This app handles:
- Crop information management
- ML-based crop recommendation
- Recommendation history tracking
"""

from django.apps import AppConfig


class CropRecommendationConfig(AppConfig):
    """Configuration for the crop_recommendation Django app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crop_recommendation'
    verbose_name = 'Crop Recommendation'
