import os
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METADATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'disease', 'metadata')
REPORT_PATH = os.path.join(PROJECT_ROOT, 'docs', 'DISEASE_DATA_QUALITY_REPORT.md')

def generate_report():
    print("Generating data quality report...")
    
    summary_path = os.path.join(METADATA_DIR, 'dataset_summary.json')
    split_path = os.path.join(METADATA_DIR, 'split_summary.json')
    
    if not os.path.exists(summary_path):
        print("Summary JSON not found. Run prepare_disease_dataset.py first.")
        return
        
    with open(summary_path, 'r') as f:
        summary = json.load(f)
        
    split_info = {}
    if os.path.exists(split_path):
        with open(split_path, 'r') as f:
            split_info = json.load(f)
            
    report = f"""# Plant Disease Data Quality Report

## Dataset Source
**Source:** PlantVillage (Community Mirror: spMohanty/PlantVillage-Dataset)
**License:** CC0 / Public Domain

## Dataset Size
- **Total Images Processed:** {summary.get('total_images_processed', 0)}
- **Valid Unique Images After Split:** {split_info.get('total_images', 0)}

## Number of Classes
- **Classes Found:** {summary.get('total_classes', 0)}

## Crop Distribution
- **Number of Unique Crops:** {summary.get('crops', 0)}
*(See `ml/disease/analysis/plots/crop_distribution.png` for visualization)*

## Image Dimensions
- **Found Dimensions:** {summary.get('image_dimensions', [])}
- **Found Formats:** {summary.get('formats', [])}

## Corrupted Images
- **Corrupted / 0-byte Images Detected:** {summary.get('corrupted_images', 0)}

## Duplicate Images
- **Exact Duplicate Copies Found (MD5):** {summary.get('exact_duplicates', 0)}
- **Duplicate Groups:** {summary.get('duplicate_groups', 0)}
- **Duplicates Dropped During Split:** {split_info.get('duplicates_dropped', 0)}

## Train/Validation/Test Split
- **Strategy:** {split_info.get('train_ratio', 0.7)*100:.0f}% Train / {split_info.get('val_ratio', 0.15)*100:.0f}% Validation / {split_info.get('test_ratio', 0.15)*100:.0f}% Test
- **Random Seed:** {split_info.get('random_seed', 'N/A')}
*(Note: Exact duplicates were removed prior to splitting to prevent data leakage across train and test sets).*

## Potential Dataset Bias & Limitations
1. **Lab Setting:** Images are predominantly taken on uniform backgrounds, which might cause the model to perform poorly on field images.
2. **Illumination:** Standardized lighting in the dataset might not represent natural sunlight variations.
3. **Class Imbalance:** Significant class imbalance exists across different crops and diseases (e.g., Tomato classes vastly outnumber others).

*(See `ml/disease/analysis/plots/` for detailed EDA visualizations).*
"""

    with open(REPORT_PATH, 'w') as f:
        f.write(report)
        
    print(f"Report generated at {REPORT_PATH}")

if __name__ == '__main__':
    generate_report()
