import os
import shutil
import json
import random
from collections import defaultdict
import hashlib

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'disease')
RAW_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')
METADATA_DIR = os.path.join(DATA_DIR, 'metadata')

RANDOM_STATE = 42
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

def hash_file(filepath):
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()
    except Exception:
        return None

def split_dataset():
    print("Starting dataset split with Stratification...")
    random.seed(RANDOM_STATE)
    
    classes = [d for d in os.listdir(RAW_DIR) if os.path.isdir(os.path.join(RAW_DIR, d))]
    
    # Setup processed directories
    for split in ['train', 'val', 'test']:
        for cls in classes:
            os.makedirs(os.path.join(PROCESSED_DIR, split, cls), exist_ok=True)
            
    hash_seen = set()
    duplicates_dropped = 0
    total_copied = 0
    
    for cls in classes:
        cls_dir = os.path.join(RAW_DIR, cls)
        files = [os.path.join(cls_dir, f) for f in os.listdir(cls_dir) if os.path.isfile(os.path.join(cls_dir, f))]
        
        # Filter duplicates first
        unique_files = []
        for f in files:
            h = hash_file(f)
            if h and h in hash_seen:
                duplicates_dropped += 1
                continue
            if h:
                hash_seen.add(h)
            unique_files.append(f)
            
        # Shuffle for random split
        random.shuffle(unique_files)
        
        n_total = len(unique_files)
        if n_total == 0:
            print(f"Warning: Class {cls} has no unique files!")
            continue
            
        n_train = int(n_total * TRAIN_RATIO)
        n_val = int(n_total * VAL_RATIO)
        
        train_files = unique_files[:n_train]
        val_files = unique_files[n_train:n_train+n_val]
        test_files = unique_files[n_train+n_val:]
        
        # Copy files
        def copy_files(file_list, split_name):
            for src in file_list:
                filename = os.path.basename(src)
                dst = os.path.join(PROCESSED_DIR, split_name, cls, filename)
                shutil.copy2(src, dst)
                
        copy_files(train_files, 'train')
        copy_files(val_files, 'val')
        copy_files(test_files, 'test')
        
        total_copied += n_total
        print(f"[{cls}] Total: {n_total} -> Train: {len(train_files)}, Val: {len(val_files)}, Test: {len(test_files)}")

    print(f"\nSplit Complete.")
    print(f"Duplicates dropped to prevent data leakage: {duplicates_dropped}")
    print(f"Total unique images processed: {total_copied}")
    
    # Save split summary
    split_summary = {
        "random_seed": RANDOM_STATE,
        "train_ratio": TRAIN_RATIO,
        "val_ratio": VAL_RATIO,
        "test_ratio": TEST_RATIO,
        "duplicates_dropped": duplicates_dropped,
        "total_images": total_copied
    }
    with open(os.path.join(METADATA_DIR, 'split_summary.json'), 'w') as f:
        json.dump(split_summary, f, indent=4)

if __name__ == '__main__':
    split_dataset()
