from rest_framework import viewsets, views, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination

from .models import Crop, CropRecommendationRequest
from .serializers import (
    CropSerializer, 
    CropRecommendationInputSerializer, 
    CropRecommendationHistorySerializer
)
from .services.recommendation_service import generate_recommendation, ModelUnavailableError


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
