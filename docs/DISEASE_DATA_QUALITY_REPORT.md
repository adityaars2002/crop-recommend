# Plant Disease Data Quality Report

## Dataset Source
**Source:** PlantVillage (Community Mirror: spMohanty/PlantVillage-Dataset)
**License:** CC0 / Public Domain

## Dataset Size
- **Total Images Processed:** 54305
- **Valid Unique Images After Split:** 54284

## Number of Classes
- **Classes Found:** 38

## Crop Distribution
- **Number of Unique Crops:** 14
*(See `ml/disease/analysis/plots/crop_distribution.png` for visualization)*

## Image Dimensions
- **Found Dimensions:** [{'width': 256, 'height': 256}]
- **Found Formats:** ['JPEG', 'PNG']

## Corrupted Images
- **Corrupted / 0-byte Images Detected:** 0

## Duplicate Images
- **Exact Duplicate Copies Found (MD5):** 21
- **Duplicate Groups:** 21
- **Duplicates Dropped During Split:** 21

## Train/Validation/Test Split
- **Strategy:** 70% Train / 15% Validation / 15% Test
- **Random Seed:** 42
*(Note: Exact duplicates were removed prior to splitting to prevent data leakage across train and test sets).*

## Potential Dataset Bias & Limitations
1. **Lab Setting:** Images are predominantly taken on uniform backgrounds, which might cause the model to perform poorly on field images.
2. **Illumination:** Standardized lighting in the dataset might not represent natural sunlight variations.
3. **Class Imbalance:** Significant class imbalance exists across different crops and diseases (e.g., Tomato classes vastly outnumber others).

*(See `ml/disease/analysis/plots/` for detailed EDA visualizations).*
