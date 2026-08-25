# Smart Agriculture System — ML Model Report

## 1. Objective
The objective of this machine learning model is to predict the most suitable crop for cultivation based on a given set of environmental and soil conditions. This forms the core of the Smart Agriculture System's recommendation engine.

## 2. Dataset
- **Name:** Crop Recommendation Dataset
- **Source:** Kaggle (Atharva Ingle)
- **Size:** 2,200 samples

## 3. Features
The model uses exactly 7 numerical features:
1. **N**: Nitrogen content in soil (kg/ha)
2. **P**: Phosphorus content in soil (kg/ha)
3. **K**: Potassium content in soil (kg/ha)
4. **temperature**: Average temperature (°C)
5. **humidity**: Relative humidity (%)
6. **ph**: Soil pH value (0-14)
7. **rainfall**: Annual rainfall (mm)

## 4. Target
The target variable is the `label` column, which contains **22 unique crop classes** (e.g., rice, maize, cotton, apple, banana). The dataset is perfectly balanced with exactly 100 samples per class.

## 5. Train/Test Strategy
The dataset was split using an 80/20 train/test split with stratification to ensure balanced classes in both sets:
- **Training Set:** 1,760 samples (80%)
- **Test Set:** 440 samples (20%) — Held out strictly for final evaluation.
- **Random State:** 42

## 6. Cross Validation
Model comparison was performed on the training set using 5-Fold `StratifiedKFold`. This ensures that each fold maintains the same class distribution as the overall training set, providing a robust estimate of model performance before touching the test set.

## 7. Models Compared
Four algorithms were evaluated:
- **Random Forest:** Ensemble of decision trees.
- **Decision Tree:** Single tree classifier.
- **K-Nearest Neighbors (KNN):** Distance-based (features were scaled using `StandardScaler` in a Pipeline).
- **Logistic Regression:** Linear classifier (features were scaled using `StandardScaler` in a Pipeline).

## 8. Results (Cross-Validation)

| Model | Mean CV Accuracy | Mean CV F1 (Weighted) |
|-------|-----------------|----------------------|
| **Random Forest** | **0.9938 ± 0.0061** | **0.9937 ± 0.0061** |
| Decision Tree | 0.9852 ± 0.0068 | 0.9852 ± 0.0068 |
| Logistic Regression | 0.9682 ± 0.0066 | 0.9678 ± 0.0068 |
| KNN | 0.9653 ± 0.0121 | 0.9650 ± 0.0124 |

## 9. Selected Model
**Random Forest Classifier** was selected as the final model because:
1. It achieved the highest cross-validation accuracy and F1 score.
2. It showed very high stability (low standard deviation) across folds.
3. It does not require feature scaling, simplifying the inference pipeline.
4. It natively provides feature importance to explain its decisions.

## 10. Hyperparameter Tuning
Hyperparameter tuning was performed on the Random Forest using `RandomizedSearchCV` across 3 folds on the training data. 
The best parameters found were:
- `n_estimators`: 100
- `max_depth`: 30
- `max_features`: log2
- `min_samples_split`: 5
- `min_samples_leaf`: 2

## 11. Final Test Results
The final tuned model was evaluated *once* on the untouched test set (440 samples) and achieved exceptional performance:
- **Accuracy:** 99.55%
- **Precision (Weighted):** 99.57%
- **Recall (Weighted):** 99.55%
- **F1 Score (Weighted):** 99.55%

## 12. Confusion Matrix
The confusion matrix (saved in `ml/evaluation/results/confusion_matrix.png`) shows nearly perfect diagonal alignment, meaning almost all predictions matched the true classes. The few errors represent extremely rare edge cases where crop environmental requirements overlap heavily.

## 13. Feature Importance
Feature importance indicates which variables the model relied on most heavily to make its splits:
1. **Rainfall:** 22.91%
2. **Humidity:** 22.21%
3. **Potassium (K):** 17.57%
4. **Phosphorus (P):** 14.68%
5. **Nitrogen (N):** 10.42%
6. **Temperature:** 7.13%
7. **pH:** 5.07%

*Analysis:* Water-related metrics (Rainfall and Humidity) are the most critical determining factors in this dataset, accounting for ~45% of the model's decision-making power. Soil pH was the least important factor overall for separating these specific 22 classes. 
*Note:* Feature importance indicates model behavior, not strict biological causation.

## 14. Limitations
- **Dataset Bias:** The dataset is highly synthetic/stylized (exactly 100 samples per crop, very distinct boundaries). Real-world agricultural data is significantly messier.
- **Missing Variables:** The model does not account for critical real-world factors like soil texture, organic matter, solar radiation, or local microclimates.
- **Not a Guarantee:** The recommendations are based on statistical patterns, not guaranteed agronomic success.

## 15. Future Improvements
- **Real-World Calibration:** Integrate actual sensor data from live farms.
- **Regional Context:** Add geographical or climate-zone features.
- **Weather API Integration:** Pull real-time humidity and rainfall rather than relying entirely on user input.
- **Expert Validation:** Have agronomists validate the boundary conditions learned by the model.
