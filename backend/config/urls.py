"""
Root URL Configuration for Smart Agriculture System.

API versioning is implemented from the start:
    /api/v1/  →  Version 1 endpoints

This allows future versions (/api/v2/) without breaking existing clients.
"""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # --- Django Admin ---
    path('admin/', admin.site.urls),

    # --- API Schema & Documentation ---
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),

    # --- API v1 ---
    path('api/v1/crops/', include('crop_recommendation.urls')),
]
