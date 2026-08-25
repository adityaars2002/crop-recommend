import math
from django.test import TestCase
from crop_recommendation.serializers import CropRecommendationInputSerializer

class SerializerTest(TestCase):
    def test_valid_input(self):
        data = {
            "nitrogen": 90, "phosphorus": 42, "potassium": 43,
            "temperature": 25.5, "humidity": 80.0, "ph": 6.5, "rainfall": 200.0
        }
        serializer = CropRecommendationInputSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_missing_fields(self):
        data = {"nitrogen": 90}
        serializer = CropRecommendationInputSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('ph', serializer.errors)

    def test_invalid_type(self):
        data = {
            "nitrogen": "abc", "phosphorus": 42, "potassium": 43,
            "temperature": 25.5, "humidity": 80.0, "ph": 6.5, "rainfall": 200.0
        }
        serializer = CropRecommendationInputSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('nitrogen', serializer.errors)

    def test_invalid_range_ph(self):
        data = {
            "nitrogen": 90, "phosphorus": 42, "potassium": 43,
            "temperature": 25.5, "humidity": 80.0, "ph": 15.0, "rainfall": 200.0
        }
        serializer = CropRecommendationInputSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('ph', serializer.errors)

    def test_nan_values(self):
        data = {
            "nitrogen": 90, "phosphorus": 42, "potassium": 43,
            "temperature": 25.5, "humidity": 80.0, "ph": math.nan, "rainfall": 200.0
        }
        serializer = CropRecommendationInputSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('ph', serializer.errors)
