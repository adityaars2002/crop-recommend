"""
Root URL Configuration for Smart Agriculture System.

API versioning is implemented from the start:
    /api/v1/  →  Version 1 endpoints

This allows future versions (/api/v2/) without breaking existing clients.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)


def health_check(request):
    """Lightweight health check endpoint for Render."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    # --- Health Check ---
    path('api/health/', health_check, name='health-check'),

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
