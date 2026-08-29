# Model Card: Plant Disease Detection

## Model Details
- **Model Name:** MobileNetV2 (Fine-tuned for Plant Disease Detection)
- **Version:** 1.0.0
- **Model Type:** Convolutional Neural Network (Image Classification)
- **Framework:** TensorFlow / Keras
- **Architecture:** Pre-trained MobileNetV2 with a custom dense classification head.

## Intended Use
- **Primary Use Case:** Classifying leaf images to detect plant diseases or confirm healthy states.
- **Target Audience:** Developers and integrators of the Smart Agriculture System.
- **Out of Scope:** This model is not intended for non-plant images or crops/diseases not present in the 38-class PlantVillage dataset.

## Training Data
- **Dataset:** PlantVillage Dataset
- **Total Images:** 54,305 (approximately)
- **Split:** 70% Train, 15% Validation, 15% Test
- **Classes:** 38 (includes 14 crop species and various healthy/diseased states)
- **Preprocessing:** Resized to 224x224x3, standard MobileNetV2 preprocessing (scaled to `[-1, 1]`).

## Evaluation Metrics (Test Set)
- **Test Accuracy:** 0.9705
- **Macro F1 Score:** 0.9657
- **Weighted F1 Score:** 0.9706
- **Test Set Size:** 8,176 images

## Training Procedure
- **Stage 1 (Baseline):** Backbone frozen. Trained classification head for 15 epochs. Validation Accuracy: 0.9515.
- **Stage 2 (Class-Weighted):** Backbone frozen. Class weights applied to handle dataset imbalance for 15 epochs. Validation Accuracy: 0.9493.
- **Stage 3 (Fine-Tuning):** Last 30 layers un-frozen. Batch Normalization layers kept frozen. Learning rate: `1e-5`. Epochs: 10. Validation Accuracy: 0.9717.
- **Hardware:** GPU-accelerated environments.

## Limitations & Risks
- **Background Bias:** The PlantVillage dataset features leaves typically photographed against controlled backgrounds. The model may perform poorly on images with complex backgrounds (e.g., leaves still on the tree with soil/sky in the background).
- **Illumination Sensitivity:** The model has not been extensively tested on images with extreme shadowing or overexposure.
- **False Confidence:** The model may output high confidence scores for out-of-distribution images (e.g., completely unrelated objects).

## Model Specifications
- **Total Parameters:** 2,306,662
- **Trainable Parameters:** 1,559,398
- **Non-trainable Parameters:** 747,264
- **Model Size:** ~33.2 MB
- **Input Shape:** `(None, 224, 224, 3)`
- **Output Shape:** `(None, 38)`
