from unittest.mock import patch
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from crop_recommendation.models import Crop, CropRecommendationRequest

class APIEndpointTests(APITestCase):
    def setUp(self):
        self.crop1 = Crop.objects.create(name="rice", min_ph=5.0, max_ph=6.5)
        self.crop2 = Crop.objects.create(name="maize")
        self.recommend_url = reverse('crop_recommendation:recommend')
        self.list_url = reverse('crop_recommendation:crop-list')
        self.history_url = reverse('crop_recommendation:recommend-history-list')
        
        self.valid_payload = {
            "nitrogen": 90, "phosphorus": 42, "potassium": 43,
            "temperature": 25.5, "humidity": 80.0, "ph": 6.5, "rainfall": 200.0
        }

    def test_crop_list_api(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 2)
        self.assertEqual(response.data['data'][0]['name'], 'maize') # Ordered alphabetically

    def test_crop_detail_api(self):
        detail_url = reverse('crop_recommendation:crop-detail', kwargs={'pk': self.crop1.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], 'rice')

    def test_crop_detail_not_found(self):
        detail_url = reverse('crop_recommendation:crop-detail', kwargs={'pk': 999})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error']['code'], 'NOT_FOUND')

    @patch('crop_recommendation.services.recommendation_service.predict_crop')
    def test_recommend_api_success(self, mock_predict):
        mock_predict.return_value = [
            {"crop": "rice", "score": 0.95},
            {"crop": "maize", "score": 0.04},
            {"crop": "cotton", "score": 0.01}
        ]
        
        response = self.client.post(self.recommend_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Test Android contract exact matches
        data = response.data['data']
        self.assertIn('recommendations', data)
        self.assertEqual(len(data['recommendations']), 3)
        
        first_rec = data['recommendations'][0]
        self.assertEqual(first_rec['rank'], 1)
        self.assertEqual(first_rec['crop']['name'], 'rice')
        self.assertEqual(first_rec['score'], 0.95)
        
    def test_recommend_api_invalid_input(self):
        invalid_payload = {"nitrogen": 90} # Missing fields
        response = self.client.post(self.recommend_url, invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error']['code'], 'VALIDATION_ERROR')
        self.assertIn('ph', response.data['error']['fields'])

    @patch('crop_recommendation.services.recommendation_service.predict_crop')
    def test_recommend_api_model_failure(self, mock_predict):
        mock_predict.side_effect = Exception("Model broken")
        response = self.client.post(self.recommend_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['error']['code'], 'MODEL_UNAVAILABLE')

    @patch('crop_recommendation.services.recommendation_service.predict_crop')
    def test_history_api(self, mock_predict):
        mock_predict.return_value = [{"crop": "rice", "score": 0.95}]
        
        # Make a request to populate history
        self.client.post(self.recommend_url, self.valid_payload, format='json')
        
        response = self.client.get(self.history_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['recommendations'][0]['crop']['name'], 'rice')
