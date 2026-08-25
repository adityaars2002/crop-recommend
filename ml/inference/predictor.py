"""
Inference Module for Crop Recommendation.

This module provides a clean interface for making predictions using the 
trained machine learning model. It handles input validation, feature 
ordering, model loading, and prediction formatting.

Usage:
    from ml.inference.predictor import predict_crop
    
    result = predict_crop(
        N=90, P=42, K=43, temperature=25.5, 
        humidity=80, ph=6.5, rainfall=200
    )
"""

import sys
import json
import logging
import joblib
from pathlib import Path
from typing import List, Dict, Union

import pandas as pd
import numpy as np

# Ensure project root is on sys.path
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from ml.config import ML_ARTIFACTS_DIR

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

MODEL_ARTIFACT_PATH = ML_ARTIFACTS_DIR / 'crop_recommendation_model.joblib'
METADATA_PATH = ML_ARTIFACTS_DIR / 'model_metadata.json'

# Global cache for the loaded model and metadata to avoid reloading on every request
_model = None
_metadata = None


def load_model_and_metadata():
    """Load the model and metadata from disk, caching them in memory."""
    global _model, _metadata
    
    if _model is not None and _metadata is not None:
        return _model, _metadata
        
    if not MODEL_ARTIFACT_PATH.exists() or not METADATA_PATH.exists():
        raise FileNotFoundError(
            "Model artifacts not found. Please train the model first using `python ml/training/train.py`."
        )
        
    try:
        _model = joblib.load(MODEL_ARTIFACT_PATH)
        with open(METADATA_PATH, 'r') as f:
            _metadata = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load model artifacts: {e}")
        raise RuntimeError(f"Model loading failed: {e}")
        
    return _model, _metadata


def predict_crop(N: float, P: float, K: float, temperature: float, 
                 humidity: float, ph: float, rainfall: float, 
                 top_k: int = 3) -> List[Dict[str, Union[str, float]]]:
    """
    Predict the most suitable crops based on environmental features.
    
    Args:
        N: Nitrogen content in soil
        P: Phosphorus content in soil
        K: Potassium content in soil
        temperature: Temperature in Celsius
        humidity: Relative humidity in %
        ph: Soil pH value
        rainfall: Rainfall in mm
        top_k: Number of top recommendations to return
        
    Returns:
        List of dictionaries containing 'crop' and 'score' (model output probability),
        sorted from highest to lowest score.
        
    Raises:
        ValueError: If inputs are invalid.
        RuntimeError: If model fails to load or predict.
    """
    # 1. Validate inputs (basic sanity checks)
    inputs = {
        'N': N, 'P': P, 'K': K, 
        'temperature': temperature, 'humidity': humidity, 
        'ph': ph, 'rainfall': rainfall
    }
    
    for name, value in inputs.items():
        if not isinstance(value, (int, float)):
            raise ValueError(f"Feature '{name}' must be a number, got {type(value).__name__}.")
            
    # pH must be technically between 0 and 14
    if ph < 0 or ph > 14:
        raise ValueError(f"pH must be between 0 and 14, got {ph}")
        
    # 2. Load model and metadata
    model, metadata = load_model_and_metadata()
    feature_order = metadata['features']
    classes = metadata['classes']
    
    # 3. Create feature array matching expected order
    features_df = pd.DataFrame([inputs], columns=feature_order)
    
    # 4. Predict probabilities
    try:
        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(features_df)[0]
            
            # Combine classes and probabilities
            results = [
                {"crop": crop_class, "score": round(float(prob), 4)} 
                for crop_class, prob in zip(classes, probabilities)
            ]
            
            # Sort by score descending
            results.sort(key=lambda x: x["score"], reverse=True)
            
            # Return top_k
            return results[:top_k]
        else:
            # Fallback if model doesn't support predict_proba (e.g. SVM without prob=True)
            prediction = model.predict(features_df)[0]
            return [{"crop": prediction, "score": 1.0}]
            
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise RuntimeError(f"Model prediction failed: {e}")


if __name__ == '__main__':
    # Simple sanity check
    print("Running predictor sanity check...")
    try:
        sample = {
            "N": 90, "P": 42, "K": 43, 
            "temperature": 25.5, "humidity": 80, 
            "ph": 6.5, "rainfall": 200
        }
        recommendations = predict_crop(**sample)
        print("\nTest Inputs:")
        for k, v in sample.items():
            print(f"  {k}: {v}")
            
        print("\nTop 3 Recommendations:")
        for rec in recommendations:
            print(f"  - {rec['crop']} (Score: {rec['score']:.4f})")
            
    except Exception as e:
        print(f"Error during sanity check: {e}")
