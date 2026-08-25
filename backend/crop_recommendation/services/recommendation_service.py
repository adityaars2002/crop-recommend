import logging
from django.db import transaction
from django.conf import settings
import sys

# Ensure ml module is accessible
if str(settings.PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(settings.PROJECT_ROOT))

try:
    from ml.inference.predictor import predict_crop
except ImportError as e:
    logging.error(f"Failed to import ML predictor: {e}")
    predict_crop = None

from crop_recommendation.models import Crop, CropRecommendationRequest, CropRecommendationResult

logger = logging.getLogger(__name__)

class ModelUnavailableError(Exception):
    pass

def generate_recommendation(input_data: dict) -> CropRecommendationRequest:
    """
    Core business logic for generating a crop recommendation.
    
    1. Maps API inputs to ML feature names.
    2. Calls the ML predictor.
    3. Looks up predicted crops in the database.
    4. Saves the request and results using a transaction.
    5. Returns the saved CropRecommendationRequest object with prefetched results.
    
    Args:
        input_data (dict): Validated input data containing nitrogen, phosphorus, etc.
        
    Returns:
        CropRecommendationRequest: The saved request object.
        
    Raises:
        ModelUnavailableError: If the ML model fails to load or predict.
    """
    if predict_crop is None:
        raise ModelUnavailableError("ML Predictor is not available.")
        
    # 1. Map to ML input names (N, P, K, etc)
    ml_inputs = {
        'N': input_data['nitrogen'],
        'P': input_data['phosphorus'],
        'K': input_data['potassium'],
        'temperature': input_data['temperature'],
        'humidity': input_data['humidity'],
        'ph': input_data['ph'],
        'rainfall': input_data['rainfall']
    }
    
    # 2. Call ML Predictor
    try:
        predictions = predict_crop(**ml_inputs, top_k=3)
    except Exception as e:
        logger.error(f"ML prediction failed: {e}")
        raise ModelUnavailableError("Crop recommendation service is temporarily unavailable.")
        
    if not predictions:
        raise ModelUnavailableError("Crop recommendation service returned no results.")

    # Extract predicted crop names
    predicted_crop_names = [p['crop'] for p in predictions]
    
    # 3. Lookup Crops in DB (bulk lookup)
    crops_qs = Crop.objects.filter(name__in=predicted_crop_names)
    crop_map = {crop.name: crop for crop in crops_qs}
    
    # Check for missing crops (Log a warning, but don't fail)
    for name in predicted_crop_names:
        if name not in crop_map:
            logger.warning(f"Predicted crop '{name}' does not exist in the database.")
            
    # 4. Save to DB atomically
    with transaction.atomic():
        # Create request record
        request_obj = CropRecommendationRequest.objects.create(
            nitrogen=input_data['nitrogen'],
            phosphorus=input_data['phosphorus'],
            potassium=input_data['potassium'],
            temperature=input_data['temperature'],
            humidity=input_data['humidity'],
            ph=input_data['ph'],
            rainfall=input_data['rainfall']
        )
        
        # Create result records
        results_to_create = []
        for i, pred in enumerate(predictions, start=1):
            crop_name = pred['crop']
            score = pred['score']
            crop_obj = crop_map.get(crop_name)
            
            results_to_create.append(
                CropRecommendationResult(
                    request=request_obj,
                    crop=crop_obj,
                    score=score,
                    rank=i
                )
            )
            
        CropRecommendationResult.objects.bulk_create(results_to_create)
        
    # Return the request object (Django will need it for the serializer)
    return request_obj
