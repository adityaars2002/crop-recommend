import pytest
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.append(PROJECT_ROOT)

from ml.disease.inference.predictor import predict_disease

# Note: These tests require the model to be trained and saved at ml/disease/artifacts/plant_disease_model.keras

@pytest.mark.skipif(not os.path.exists(os.path.join(PROJECT_ROOT, 'ml', 'disease', 'artifacts', 'plant_disease_model.keras')), 
                    reason="Model not trained yet")
def test_valid_image_prediction():
    # Find a valid test image
    test_dir = os.path.join(PROJECT_ROOT, 'data', 'disease', 'processed', 'test')
    class_dirs = os.listdir(test_dir)
    if not class_dirs:
        pytest.skip("Test dataset empty")
        
    sample_img = os.path.join(test_dir, class_dirs[0], os.listdir(os.path.join(test_dir, class_dirs[0]))[0])
    
    top_pred, top3 = predict_disease(sample_img)
    
    assert top_pred is not None
    assert 'crop' in top_pred
    assert 'disease' in top_pred
    assert 'status' in top_pred
    assert 'score' in top_pred
    
    assert 0.0 <= top_pred['score'] <= 1.0
    
    assert len(top3) == 3
    assert top3[0]['score'] >= top3[1]['score']
    assert top3[1]['score'] >= top3[2]['score']

def test_invalid_image_path():
    with pytest.raises(FileNotFoundError):
        predict_disease("nonexistent_image.jpg")

@pytest.mark.skipif(not os.path.exists(os.path.join(PROJECT_ROOT, 'ml', 'disease', 'artifacts', 'plant_disease_model.keras')), 
                    reason="Model not trained yet")
def test_unsupported_image_format(tmp_path):
    # Create a fake image file (text file with .jpg extension)
    fake_img = tmp_path / "fake.jpg"
    fake_img.write_text("This is not an image")
    
    with pytest.raises(ValueError):
        predict_disease(str(fake_img))
