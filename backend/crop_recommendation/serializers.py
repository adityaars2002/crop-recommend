from rest_framework import serializers
from .models import Crop, CropRecommendationRequest, CropRecommendationResult
import math

class CropSerializer(serializers.ModelSerializer):
    """Serializer for the Crop model."""
    class Meta:
        model = Crop
        fields = '__all__'


class CropRecommendationInputSerializer(serializers.Serializer):
    """
    Validates input for crop recommendation.
    Uses human-readable names as requested.
    """
    nitrogen = serializers.FloatField(min_value=0.0)
    phosphorus = serializers.FloatField(min_value=0.0)
    potassium = serializers.FloatField(min_value=0.0)
    temperature = serializers.FloatField()
    humidity = serializers.FloatField(min_value=0.0, max_value=100.0)
    ph = serializers.FloatField(min_value=0.0, max_value=14.0)
    rainfall = serializers.FloatField(min_value=0.0)

    def validate(self, data):
        """Ensure no NaNs or Infinities."""
        for key, value in data.items():
            if math.isnan(value) or math.isinf(value):
                raise serializers.ValidationError({
                    key: f"Value for {key} cannot be NaN or Infinity."
                })
        return data


class CropRecommendationResultSerializer(serializers.ModelSerializer):
    """Serializer for the nested results in a recommendation response."""
    # We embed the full crop details inside the result
    crop = CropSerializer(read_only=True)
    
    # If crop is somehow null, we still want to output something, but it's handled by ModelSerializer (returns null).
    
    class Meta:
        model = CropRecommendationResult
        fields = ('rank', 'crop', 'score')


class CropRecommendationHistorySerializer(serializers.ModelSerializer):
    """Serializer for the recommendation history."""
    input = serializers.SerializerMethodField()
    recommendations = CropRecommendationResultSerializer(many=True, read_only=True)

    class Meta:
        model = CropRecommendationRequest
        fields = ('id', 'created_at', 'input', 'recommendations')

    def get_input(self, obj):
        return {
            "nitrogen": obj.nitrogen,
            "phosphorus": obj.phosphorus,
            "potassium": obj.potassium,
            "temperature": obj.temperature,
            "humidity": obj.humidity,
            "ph": obj.ph,
            "rainfall": obj.rainfall
        }
