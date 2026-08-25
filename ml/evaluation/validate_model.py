"""
Model Artifact Validation Script.

This script loads the saved ML model artifact and its metadata to verify
that it was saved correctly and can perform predictions. This acts as an
automated sanity check for the finalized model before it is used by the API.

Usage:
    python ml/evaluation/validate_model.py
"""

import sys
import json
import logging
import joblib
from pathlib import Path

# Ensure project root is on sys.path
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from ml.config import ML_ARTIFACTS_DIR
from ml.inference.predictor import predict_crop, load_model_and_metadata

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting model artifact validation...")
    
    # 1. Verify files exist
    model_path = ML_ARTIFACTS_DIR / 'crop_recommendation_model.joblib'
    metadata_path = ML_ARTIFACTS_DIR / 'model_metadata.json'
    
    if not model_path.exists():
        logger.error(f"[FAILED] Model artifact not found at {model_path}")
        sys.exit(1)
        
    if not metadata_path.exists():
        logger.error(f"[FAILED] Metadata not found at {metadata_path}")
        sys.exit(1)
        
    logger.info(f"✓ Artifact files found in {ML_ARTIFACTS_DIR.name}/")
    
    # 2. Load artifacts
    try:
        model, metadata = load_model_and_metadata()
        logger.info("✓ Model loaded successfully")
        logger.info("✓ Metadata loaded successfully")
    except Exception as e:
        logger.error(f"[FAILED] Failed to load artifacts: {e}")
        sys.exit(1)
        
    # 3. Verify metadata structure
    expected_keys = ['model_name', 'model_version', 'features', 'target', 'classes']
    missing_keys = [k for k in expected_keys if k not in metadata]
    if missing_keys:
        logger.error(f"[FAILED] Metadata missing expected keys: {missing_keys}")
        sys.exit(1)
        
    logger.info("✓ Metadata structure verified")
    
    # 4. Perform sample prediction
    try:
        sample = {
            "N": 90, "P": 42, "K": 43, 
            "temperature": 25.5, "humidity": 80, 
            "ph": 6.5, "rainfall": 200
        }
        recommendations = predict_crop(**sample)
        
        if not recommendations:
            logger.error("[FAILED] Prediction returned empty list.")
            sys.exit(1)
            
        if len(recommendations) > 3:
            logger.error(f"[FAILED] Prediction returned {len(recommendations)} items instead of max 3.")
            sys.exit(1)
            
        first = recommendations[0]
        if 'crop' not in first or 'score' not in first:
            logger.error("[FAILED] Prediction missing 'crop' or 'score' keys.")
            sys.exit(1)
            
        if first['crop'] not in metadata['classes']:
            logger.error(f"[FAILED] Predicted crop '{first['crop']}' not in known classes.")
            sys.exit(1)
            
        # Verify sorting
        scores = [r['score'] for r in recommendations]
        if scores != sorted(scores, reverse=True):
            logger.error("[FAILED] Predictions are not sorted by score descending.")
            sys.exit(1)
            
        logger.info("✓ Sample prediction successful and properly formatted")
        
    except Exception as e:
        logger.error(f"[FAILED] Sample prediction failed: {e}")
        sys.exit(1)
        
    logger.info("========================================")
    logger.info("[SUCCESS] Model artifact validation passed.")
    logger.info("========================================")

if __name__ == '__main__':
    main()
