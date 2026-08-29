import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array

# Cache the model and metadata in memory for repeated inference calls
_model = None
_class_mapping = None

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
METADATA_DIR = os.path.join(PROJECT_ROOT, 'ml', 'disease', 'metadata')
ARTIFACTS_DIR = os.path.join(PROJECT_ROOT, 'ml', 'disease', 'artifacts')

MIN_PREDICTION_SCORE = 0.5  # Configurable threshold

def load_inference_resources():
    global _model, _class_mapping
    
    if _model is None:
        model_path = os.path.join(ARTIFACTS_DIR, 'plant_disease_model.keras')
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")
        _model = tf.keras.models.load_model(model_path)
        
    if _class_mapping is None:
        mapping_path = os.path.join(METADATA_DIR, 'class_mapping.json')
        with open(mapping_path, 'r') as f:
            _class_mapping = json.load(f)

def predict_disease(image_path):
    """
    Predicts the crop disease from an image.
    Returns the top prediction and a list of top 3 predictions.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at {image_path}")
        
    load_inference_resources()
    
    try:
        img = load_img(image_path, target_size=(224, 224))
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
    except Exception as e:
        raise ValueError(f"Invalid or unsupported image format: {e}")
        
    preds = _model.predict(img_array, verbose=0)[0]
    
    # Get top 3 indices
    top3_idx = np.argsort(preds)[-3:][::-1]
    
    top3_predictions = []
    for idx in top3_idx:
        meta = _class_mapping[str(idx)]
        score = float(preds[idx])
        
        status = meta['status']
        if score < MIN_PREDICTION_SCORE:
            status = "uncertain"
            
        top3_predictions.append({
            "class_name": meta['class_name'],
            "crop": meta['crop'],
            "disease": meta['disease'],
            "status": status,
            "score": score
        })
        
    top_prediction = top3_predictions[0]
    
    return top_prediction, top3_predictions
