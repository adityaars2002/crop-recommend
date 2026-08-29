from rest_framework import viewsets, views, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination

from .models import Crop, CropRecommendationRequest
from .serializers import (
    CropSerializer, 
    CropRecommendationInputSerializer, 
    CropRecommendationHistorySerializer,
    DiseasePredictionInputSerializer
)
from .services.recommendation_service import generate_recommendation, ModelUnavailableError

import os
import sys
import tempfile
import logging
from rest_framework.parsers import MultiPartParser, FormParser

logger = logging.getLogger(__name__)

# Ensure ml directory can be imported
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

try:
    from ml.disease.inference.predictor import predict_disease
except ImportError:
    logger.error("Failed to import predict_disease from ml.disease.inference.predictor")
    predict_disease = None


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CropViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for viewing supported crops.
    """
    queryset = Crop.objects.all()
    serializer_class = CropSerializer
    pagination_class = StandardResultsSetPagination

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        # Wrap response in standard Phase 4 envelope
        # response.data contains 'results' due to pagination
        return Response({
            "success": True,
            "data": response.data['results'],
            "pagination": {
                "count": response.data['count'],
                "next": response.data['next'],
                "previous": response.data['previous']
            }
        })

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return Response({
            "success": True,
            "data": response.data
        })


class CropRecommendationHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for viewing recommendation history.
    """
    queryset = CropRecommendationRequest.objects.prefetch_related('recommendations__crop').all()
    serializer_class = CropRecommendationHistorySerializer
    pagination_class = StandardResultsSetPagination

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            "success": True,
            "data": response.data['results'],
            "pagination": {
                "count": response.data['count'],
                "next": response.data['next'],
                "previous": response.data['previous']
            }
        })

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return Response({
            "success": True,
            "data": response.data
        })


class CropRecommendationView(views.APIView):
    """
    API endpoint to generate crop recommendations using the ML model.
    """
    
    @extend_schema(
        request=CropRecommendationInputSerializer,
        responses={200: CropRecommendationHistorySerializer},
        description="Submit environmental data to receive top 3 crop recommendations.",
        examples=[
            OpenApiExample(
                "Example Input",
                value={
                    "nitrogen": 90,
                    "phosphorus": 42,
                    "potassium": 43,
                    "temperature": 25.5,
                    "humidity": 80.0,
                    "ph": 6.5,
                    "rainfall": 200.0
                }
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        # 1. Validate Input
        serializer = CropRecommendationInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # 2. Call Service Layer
            request_record = generate_recommendation(serializer.validated_data)
            
            # 3. Serialize Output
            output_serializer = CropRecommendationHistorySerializer(request_record)
            
            # 4. Return formatted response
            return Response(
                {
                    "success": True,
                    "data": output_serializer.data
                },
                status=status.HTTP_200_OK
            )
            
        except ModelUnavailableError as e:
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "MODEL_UNAVAILABLE",
                        "message": str(e)
                    }
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Unexpected error in CropRecommendationView")
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "An unexpected error occurred while processing the recommendation."
                    }
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DiseasePredictionView(views.APIView):
    """
    API endpoint to predict plant disease from an uploaded leaf image.
    """
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request=DiseasePredictionInputSerializer,
        responses={200: dict},
        description="Upload a plant leaf image to predict its disease and status.",
    )
    def post(self, request, *args, **kwargs):
        serializer = DiseasePredictionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        image_file = serializer.validated_data['image']
        temp_path = None
        
        try:
            if predict_disease is None:
                return Response({
                    "success": False,
                    "error": {
                        "code": "MODEL_UNAVAILABLE",
                        "message": "ML inference module is not available on this server."
                    }
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            # Save uploaded image to a temporary file for the ML inference script
            fd, temp_path = tempfile.mkstemp(suffix=".jpg")
            with os.fdopen(fd, 'wb') as f:
                for chunk in image_file.chunks():
                    f.write(chunk)
                    
            # Call inference
            top_prediction, top3_predictions = predict_disease(temp_path)
            
            return Response({
                "success": True,
                "data": {
                    "prediction": top_prediction,
                    "top_3": top3_predictions
                }
            }, status=status.HTTP_200_OK)
            
        except FileNotFoundError as e:
            logger.error(f"Model file not found: {e}")
            return Response({
                "success": False,
                "error": {
                    "code": "MODEL_NOT_FOUND",
                    "message": "The plant disease model is not available."
                }
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        except ValueError as e:
            return Response({
                "success": False,
                "error": {
                    "code": "INVALID_IMAGE",
                    "message": str(e)
                }
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.exception("Unexpected error during disease prediction")
            return Response({
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred while predicting the disease."
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception as e:
                    logger.error(f"Failed to clean up temporary file {temp_path}: {e}")
