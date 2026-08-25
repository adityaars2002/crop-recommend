from unittest.mock import patch
from django.test import TestCase
from crop_recommendation.models import Crop, CropRecommendationRequest, CropRecommendationResult
from crop_recommendation.services.recommendation_service import generate_recommendation, ModelUnavailableError

class ServiceTest(TestCase):
    def setUp(self):
        self.crop1 = Crop.objects.create(name="rice")
        self.crop2 = Crop.objects.create(name="maize")
        self.input_data = {
            "nitrogen": 90, "phosphorus": 42, "potassium": 43,
            "temperature": 25.5, "humidity": 80.0, "ph": 6.5, "rainfall": 200.0
        }

    @patch('crop_recommendation.services.recommendation_service.predict_crop')
    def test_generate_recommendation_success(self, mock_predict):
        # Mock ML output
        mock_predict.return_value = [
            {"crop": "rice", "score": 0.95},
            {"crop": "maize", "score": 0.04},
            {"crop": "cotton", "score": 0.01}  # cotton is not in DB yet
        ]

        req = generate_recommendation(self.input_data)
        
        # Verify request saved
        self.assertIsInstance(req, CropRecommendationRequest)
        self.assertEqual(req.nitrogen, 90)

        # Verify results saved (including missing crop handling)
        results = req.recommendations.all().order_by('rank')
        self.assertEqual(results.count(), 3)
        
        self.assertEqual(results[0].crop, self.crop1)
        self.assertEqual(results[0].rank, 1)
        
        self.assertEqual(results[1].crop, self.crop2)
        
        # cotton doesn't exist, so crop should be None
        self.assertIsNone(results[2].crop)
        self.assertEqual(results[2].score, 0.01)

    @patch('crop_recommendation.services.recommendation_service.predict_crop')
    def test_ml_failure_raises_error(self, mock_predict):
        mock_predict.side_effect = Exception("Model exploded")

        with self.assertRaises(ModelUnavailableError):
            generate_recommendation(self.input_data)
