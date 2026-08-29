# Plant Disease Model Report

## 1. Objective
Train and evaluate a deep learning model for classifying plant diseases across 38 categories using transfer learning on MobileNetV2.

## 2. Dataset
- **Source:** PlantVillage Dataset
- **Size:** 54,284 valid unique images (38 classes, 14 crops)
- **Split:** 70% Train / 15% Validation / 15% Test
- **Seed:** 42

## 3. Dataset limitations
The PlantVillage dataset consists almost entirely of leaves photographed in controlled laboratory environments with uniform backgrounds. 
Models trained exclusively on this data may overfit to the background and lighting conditions, making them perform suboptimally on real-world field photographs containing soil, shadows, and multiple overlapping leaves.

## 4. Preprocessing
- **Resizing:** Images are dynamically resized to 224x224x3 using TensorFlow data pipelines.
- **Normalization:** `tf.keras.applications.mobilenet_v2.preprocess_input` is applied to scale pixel values appropriately for MobileNetV2 (typically to the range [-1, 1]).

## 5. Data augmentation
Applied only to the training set to prevent overfitting and improve generalization:
- Random Horizontal Flip
- Random Rotation (10%)
- Random Zoom (10%)
- Random Translation (10%)
- Random Contrast (10%)

## 6. Model architecture
- **Backbone:** MobileNetV2 (Pretrained on ImageNet, top fully-connected layers removed)
- **Head:**
  - GlobalAveragePooling2D
  - Dropout (20%)
  - Dense (38 classes, Softmax activation)

## 7. Transfer learning strategy
Three-stage training approach:
1. **Stage 1 (Baseline):** Backbone frozen. Train classification head only.
2. **Stage 2 (Class Weights):** Same as Stage 1 but incorporating balanced class weights to address dataset imbalance.
3. **Stage 3 (Fine-tuning):** Unfreeze the top portion of the backbone and train with a significantly reduced learning rate (1e-5) to fine-tune features specifically for plant diseases. BatchNormalization layers remain frozen to preserve running statistics.

## 8. Baseline experiment
- **Validation Accuracy:** 0.9515
- **Validation Loss:** 0.1542
- **Notes:** Stage 1 — All backbone layers frozen, classification head trained for 15 epochs.

## 9. Class-weight experiment
- **Validation Accuracy:** 0.9493
- **Validation Loss:** 0.1568
- **Notes:** Stage 2 — Class weights applied to handle imbalance, backbone still frozen.

## 10. Fine-tuning experiment
- **Validation Accuracy:** 0.9717
- **Validation Loss:** 0.0834
- **Notes:** Stage 3 — Last 30 layers unfrozen, BatchNormalization layers kept frozen, learning rate 1e-5.

## 11. Model comparison
The experiments are compared based on **Validation Accuracy** and **Validation Loss**. The best model is selected without referencing the Test Set.

## 12. Final model selection
The final selected model is saved to `ml/disease/artifacts/plant_disease_model.keras`.

## 13. Test performance
Evaluated on the held-out test set (8,176 images):
- **Accuracy:** 0.9705 (97.05%)
- **Macro F1:** 0.9657
- **Weighted F1:** 0.9706

## 14. Confusion matrix analysis
*(See `ml/disease/evaluation/plots/confusion_matrix.png`)*
- Discussion points to be added based on empirical confusion matrix results (e.g., commonly confused diseases within the same crop).

## 15. Per-class performance
*(See `ml/disease/evaluation/per_class_metrics.csv`)*

## 16. Crop-level performance
*(See `ml/disease/evaluation/crop_level_metrics.csv`)*

## 17. Healthy vs diseased analysis
*(See `ml/disease/evaluation/status_metrics.csv`)*

## 18. Misclassified examples
A sample of incorrect predictions (with probabilities) is saved in `ml/disease/evaluation/misclassified/` to facilitate error analysis.

## 19. Model size
- **Total Parameters:** 2,306,662
- **Trainable Parameters:** 1,559,398
- **Non-trainable Parameters:** 747,264
- **Model File Size:** ~33.2 MB

## 20. Limitations
- **Prototype Status:** The model demonstrates high capability on the dataset distribution, but lacks robustness against out-of-distribution (OOD) field samples.
- **Overconfident Predictions:** Neural networks tend to be overconfident even when incorrect. Inference thresholds (e.g., `<0.5 = uncertain`) should be calibrated using a temperature scaling method before production.

## 21. Future improvements
- Collect or synthesize diverse field backgrounds.
- Employ test-time augmentation (TTA).
- Deploy using TensorFlow Lite for on-device mobile inference (Phase 8+).
