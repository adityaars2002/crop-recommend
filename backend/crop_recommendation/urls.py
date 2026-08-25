from django.urls import path
from .views import (
    CropViewSet,
    CropRecommendationHistoryViewSet,
    CropRecommendationView
)

app_name = 'crop_recommendation'

urlpatterns = [
    path('recommend/', CropRecommendationView.as_view(), name='recommend'),
    path('recommendations/history/', CropRecommendationHistoryViewSet.as_view({'get': 'list'}), name='recommend-history-list'),
    path('recommendations/history/<int:pk>/', CropRecommendationHistoryViewSet.as_view({'get': 'retrieve'}), name='recommend-history-detail'),
    path('', CropViewSet.as_view({'get': 'list'}), name='crop-list'),
    path('<int:pk>/', CropViewSet.as_view({'get': 'retrieve'}), name='crop-detail'),
]
