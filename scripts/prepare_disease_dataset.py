import os
import glob
import json
import hashlib
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set directories
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'disease')
RAW_DIR = os.path.join(DATA_DIR, 'raw')
METADATA_DIR = os.path.join(DATA_DIR, 'metadata')
ML_METADATA_DIR = os.path.join(PROJECT_ROOT, 'ml', 'disease', 'metadata')
ML_ANALYSIS_DIR = os.path.join(PROJECT_ROOT, 'ml', 'disease', 'analysis')
PLOTS_DIR = os.path.join(ML_ANALYSIS_DIR, 'plots')

# Create necessary directories
os.makedirs(METADATA_DIR, exist_ok=True)
os.makedirs(ML_METADATA_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)

def parse_class_name(class_name):
    """Parses PlantVillage class names."""
    if '___' in class_name:
        parts = class_name.split('___')
        crop = parts[0].replace('_', ' ').strip()
        disease_part = parts[1].strip()
        
        if disease_part.lower() == 'healthy':
            status = 'healthy'
            disease = 'healthy'
        else:
            status = 'diseased'
            disease = disease_part.replace('_', ' ').strip()
    else:
        # Fallback for unexpected formats
        crop = class_name
        disease = 'unknown'
        status = 'unknown'
        
    return crop, disease, status

def hash_file(filepath):
    """Returns MD5 hash of a file."""
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()
    except Exception:
        return None

def main():
    print("Starting dataset preparation...")
    
    # Move files from downloaded zip or clone if needed
    potential_src_dirs = [
        os.path.join(PROJECT_ROOT, 'temp_plantvillage', 'raw', 'color'),
        os.path.join(PROJECT_ROOT, 'PlantVillage-Dataset-master', 'raw', 'color'),
        os.path.join(PROJECT_ROOT, 'PlantVillage-Dataset-master', 'PlantVillage-Dataset-master', 'raw', 'color')
    ]
    
    for temp_color_dir in potential_src_dirs:
        if os.path.exists(temp_color_dir):
            print(f"Moving downloaded dataset from {temp_color_dir} to data/disease/raw...")
            import shutil
            os.makedirs(RAW_DIR, exist_ok=True)
            for cls_dir in os.listdir(temp_color_dir):
                src_cls_dir = os.path.join(temp_color_dir, cls_dir)
                dst_cls_dir = os.path.join(RAW_DIR, cls_dir)
                if os.path.isdir(src_cls_dir):
                    if not os.path.exists(dst_cls_dir):
                        shutil.move(src_cls_dir, dst_cls_dir)
            print("Move completed.")
            break
    
    if not os.path.exists(RAW_DIR):
        print(f"Error: {RAW_DIR} does not exist.")
        return

    classes = [d for d in os.listdir(RAW_DIR) if os.path.isdir(os.path.join(RAW_DIR, d))]
    classes.sort()
    
    class_mapping = {}
    class_names = []
    
    dataset_records = []
    corrupted_files = []
    hash_dict = {} # hash -> list of file paths
    
    print(f"Found {len(classes)} classes.")
    
    for i, cls in enumerate(classes):
        class_names.append(cls)
        crop, disease, status = parse_class_name(cls)
        
        class_mapping[str(i)] = {
            "class_name": cls,
            "crop": crop,
            "disease": disease,
            "status": status
        }
        
        cls_dir = os.path.join(RAW_DIR, cls)
        files = glob.glob(os.path.join(cls_dir, '*.*'))
        
        for f in files:
            size = os.path.getsize(f)
            if size == 0:
                corrupted_files.append({"file": f, "reason": "0-byte"})
                continue
                
            try:
                with Image.open(f) as img:
                    img.verify() # Verify it is an image
                
                # Reopen to get details, verify() closes the file sometimes or makes it unreadable
                with Image.open(f) as img:
                    width, height = img.size
                    mode = img.mode
                    fmt = img.format
                    
                file_hash = hash_file(f)
                
                if file_hash:
                    if file_hash not in hash_dict:
                        hash_dict[file_hash] = []
                    hash_dict[file_hash].append(f)
                    
                dataset_records.append({
                    "file_path": f,
                    "class_name": cls,
                    "crop": crop,
                    "disease": disease,
                    "status": status,
                    "width": width,
                    "height": height,
                    "mode": mode,
                    "format": fmt,
                    "hash": file_hash
                })
                
            except Exception as e:
                corrupted_files.append({"file": f, "reason": str(e)})

    # Save class mappings
    with open(os.path.join(METADATA_DIR, 'class_mapping.json'), 'w') as f:
        json.dump(class_mapping, f, indent=4)
        
    with open(os.path.join(ML_METADATA_DIR, 'class_mapping.json'), 'w') as f:
        json.dump(class_mapping, f, indent=4)
        
    with open(os.path.join(ML_METADATA_DIR, 'class_names.json'), 'w') as f:
        json.dump(class_names, f, indent=4)
        
    print(f"Generated metadata for {len(classes)} classes.")
    
    # Duplicate analysis
    exact_duplicates_count = 0
    duplicate_groups = []
    
    for h, paths in hash_dict.items():
        if len(paths) > 1:
            exact_duplicates_count += (len(paths) - 1)
            duplicate_groups.append(paths)
            
    print(f"Found {exact_duplicates_count} duplicate files.")
    
    df = pd.DataFrame(dataset_records)
    
    # Generate Summary
    summary = {
        "dataset_name": "PlantVillage",
        "total_images_processed": len(df),
        "total_classes": len(classes),
        "corrupted_images": len(corrupted_files),
        "exact_duplicates": exact_duplicates_count,
        "duplicate_groups": len(duplicate_groups),
        "crops": df['crop'].nunique() if not df.empty else 0,
        "diseases": df['disease'].nunique() if not df.empty else 0,
        "image_dimensions": df[['width', 'height']].drop_duplicates().to_dict('records') if not df.empty else [],
        "formats": df['format'].unique().tolist() if not df.empty else []
    }
    
    with open(os.path.join(METADATA_DIR, 'dataset_summary.json'), 'w') as f:
        json.dump(summary, f, indent=4)
        
    if df.empty:
        print("No valid images found. Exiting.")
        return
        
    # EDA Plots
    sns.set_theme(style="whitegrid")
    
    # 1. Class Distribution
    plt.figure(figsize=(15, 8))
    sns.countplot(data=df, y='class_name', order=df['class_name'].value_counts().index, palette="viridis")
    plt.title('Class Distribution')
    plt.xlabel('Number of Images')
    plt.ylabel('Class')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'class_distribution.png'))
    plt.close()
    
    # 2. Crop Distribution
    plt.figure(figsize=(12, 6))
    sns.countplot(data=df, x='crop', order=df['crop'].value_counts().index, palette="Set2")
    plt.title('Crop Distribution')
    plt.xlabel('Crop')
    plt.ylabel('Number of Images')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'crop_distribution.png'))
    plt.close()
    
    # 3. Healthy vs Diseased
    plt.figure(figsize=(8, 6))
    sns.countplot(data=df, x='status', palette="pastel")
    plt.title('Healthy vs Diseased Images')
    plt.xlabel('Status')
    plt.ylabel('Number of Images')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'healthy_vs_diseased.png'))
    plt.close()
    
    # 4. Sample Images Grid
    # Select up to 16 classes, 1 image each
    sample_classes = df['class_name'].unique()[:16]
    
    plt.figure(figsize=(16, 12))
    for i, cls in enumerate(sample_classes):
        img_path = df[df['class_name'] == cls]['file_path'].iloc[0]
        try:
            img = Image.open(img_path)
            plt.subplot(4, 4, i+1)
            plt.imshow(img)
            plt.title(cls[:30] + '..' if len(cls)>30 else cls, fontsize=10)
            plt.axis('off')
        except Exception:
            pass
            
    plt.suptitle('Sample Images from PlantVillage Dataset', fontsize=16)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'sample_images.png'))
    plt.close()
    
    print("Dataset preparation and analysis complete!")
    print(f"Corrupted files: {len(corrupted_files)}")
    print(f"Duplicates: {exact_duplicates_count}")

if __name__ == '__main__':
    main()
