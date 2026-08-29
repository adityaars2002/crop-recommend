# Plant Disease Dataset

## 1. Overview
The dataset selected for the Plant Disease Detection module is the **PlantVillage** dataset, which is a widely used benchmark dataset for agricultural machine learning.

- **Dataset Name:** PlantVillage
- **Source:** Originally published by Hughes and Salathe, currently accessed via the standard community mirror maintained by Sharada Mohanty.
- **URL/Source:** [GitHub - spMohanty/PlantVillage-Dataset](https://github.com/spMohanty/PlantVillage-Dataset)
- **License:** CC0 / Public Domain
- **Total Images:** ~54,300 (Raw color images)
- **Total Classes:** 38
- **Format:** RGB Images (mostly 256x256 in `.jpg` / `.JPG` formats)

## 2. Categories

### Crops Represented
- Apple
- Blueberry
- Cherry (including sour)
- Corn (maize)
- Grape
- Orange
- Peach
- Pepper (bell)
- Potato
- Raspberry
- Soybean
- Squash
- Strawberry
- Tomato

### Status Categories
Each crop includes:
- **Healthy** leaf images.
- **Diseased** leaf images (various diseases specific to the crop).

## 3. Dataset Limitations
While the PlantVillage dataset is excellent for initial model training and validation, it has several critical limitations:
1. **Lab Setting Bias:** The vast majority of images were taken in a controlled environment with a uniform (gray/black) background. The model might learn to associate the background with certain predictions rather than the leaf features.
2. **Real-World Generalization:** A model trained strictly on PlantVillage may struggle when applied to real-world images taken in the field (which include diverse lighting, overlapping leaves, soil backgrounds, and shadows).
3. **Class Imbalance:** Certain crops (like Tomatoes) have significantly more images and disease variants than others (like Raspberries).

*(Note: Data distributions and detailed quality reports are generated dynamically and saved in `DISEASE_DATA_QUALITY_REPORT.md` and `ml/disease/analysis/plots/`).*
