from django.test import TestCase
from django.db.utils import IntegrityError
from crop_recommendation.models import Crop, CropRecommendationRequest, CropRecommendationResult

class CropModelTest(TestCase):
    def test_crop_creation(self):
        crop = Crop.objects.create(name="Test Crop", min_ph=5.5, max_ph=6.5)
        self.assertEqual(crop.name, "Test Crop")
        self.assertEqual(crop.min_ph, 5.5)

    def test_ph_constraint(self):
        with self.assertRaises(IntegrityError):
            # min_ph > max_ph should violate constraint
            Crop.objects.create(name="Invalid Crop", min_ph=7.0, max_ph=5.0)

class RecommendationHistoryTest(TestCase):
    def setUp(self):
        self.crop = Crop.objects.create(name="rice")

    def test_recommendation_flow(self):
        req = CropRecommendationRequest.objects.create(
            nitrogen=90, phosphorus=40, potassium=40,
            temperature=25, humidity=80, ph=6.5, rainfall=200
        )
        self.assertEqual(req.nitrogen, 90)

        res = CropRecommendationResult.objects.create(
            request=req, crop=self.crop, score=0.95, rank=1
        )
        self.assertEqual(res.rank, 1)
        self.assertEqual(res.crop.name, "rice")

    def test_unique_rank_constraint(self):
        req = CropRecommendationRequest.objects.create(
            nitrogen=90, phosphorus=40, potassium=40,
            temperature=25, humidity=80, ph=6.5, rainfall=200
        )
        CropRecommendationResult.objects.create(
            request=req, crop=self.crop, score=0.95, rank=1
        )
        with self.assertRaises(IntegrityError):
            CropRecommendationResult.objects.create(
                request=req, crop=self.crop, score=0.85, rank=1
            )
