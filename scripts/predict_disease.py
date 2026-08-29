import sys
import os
import argparse

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from ml.disease.inference.predictor import predict_disease

def main():
    parser = argparse.ArgumentParser(description="Predict plant disease from an image.")
    parser.add_argument("image_path", help="Path to the leaf image.")
    args = parser.parse_args()

    image_path = args.image_path
    
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        sys.exit(1)

    print("Loading model and predicting...\n")
    try:
        top_prediction, top3_predictions = predict_disease(image_path)
    except Exception as e:
        print(f"Error during prediction: {e}")
        sys.exit(1)

    print(f"Crop: {top_prediction['crop']}")
    print(f"Disease: {top_prediction['disease']}")
    print(f"Status: {top_prediction['status']}")
    print(f"Prediction Score: {top_prediction['score']:.4f}\n")

    print("Top 3:")
    for i, pred in enumerate(top3_predictions):
        print(f"{i+1}. {pred['crop']} - {pred['disease']} - {pred['score']:.4f}")

if __name__ == "__main__":
    main()
