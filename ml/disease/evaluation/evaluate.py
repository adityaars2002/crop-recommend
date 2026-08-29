import os
import json
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support
import matplotlib.pyplot as plt
import seaborn as sns
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import time
import shutil

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
TEST_DIR = os.path.join(PROJECT_ROOT, 'data', 'disease', 'processed', 'test')
METADATA_DIR = os.path.join(PROJECT_ROOT, 'ml', 'disease', 'metadata')
ARTIFACTS_DIR = os.path.join(PROJECT_ROOT, 'ml', 'disease', 'artifacts')
EVALUATION_DIR = os.path.join(PROJECT_ROOT, 'ml', 'disease', 'evaluation')
PLOTS_DIR = os.path.join(EVALUATION_DIR, 'plots')
MISCLASSIFIED_DIR = os.path.join(EVALUATION_DIR, 'misclassified')

os.makedirs(PLOTS_DIR, exist_ok=True)
os.makedirs(MISCLASSIFIED_DIR, exist_ok=True)

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32

def load_class_names():
    with open(os.path.join(METADATA_DIR, 'class_names.json'), 'r') as f:
        return json.load(f)
        
def load_class_mapping():
    with open(os.path.join(METADATA_DIR, 'class_mapping.json'), 'r') as f:
        return json.load(f)

def main():
    print("Starting final model evaluation on TEST set...")
    start_time = time.time()
    
    model_path = os.path.join(ARTIFACTS_DIR, 'plant_disease_model.keras')
    if not os.path.exists(model_path):
        print(f"Final model not found at {model_path}. Run compare_experiments.py first.")
        return
        
    model = tf.keras.models.load_model(model_path)
    
    test_ds = tf.keras.utils.image_dataset_from_directory(
        TEST_DIR,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        shuffle=False, # Important for metric mapping
        label_mode='categorical'
    )
    
    class_names = load_class_names()
    class_mapping = load_class_mapping()
    
    print("Generating predictions...")
    y_true = []
    y_pred = []
    y_pred_probs = []
    file_paths = test_ds.file_paths
    
    for images, labels in test_ds:
        preds = model.predict(images, verbose=0)
        y_pred_probs.extend(preds)
        y_pred.extend(np.argmax(preds, axis=1))
        y_true.extend(np.argmax(labels.numpy(), axis=1))
        
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    # ---------------------------------------------------------
    # 1. Classification Report & F1
    # ---------------------------------------------------------
    report_dict = classification_report(y_true, y_pred, target_names=class_names, output_dict=True)
    report_text = classification_report(y_true, y_pred, target_names=class_names)
    
    with open(os.path.join(EVALUATION_DIR, 'classification_report.txt'), 'w') as f:
        f.write(report_text)
        
    # ---------------------------------------------------------
    # 2. Confusion Matrix
    # ---------------------------------------------------------
    cm = confusion_matrix(y_true, y_pred)
    cm_norm = confusion_matrix(y_true, y_pred, normalize='true')
    
    plt.figure(figsize=(20, 20))
    sns.heatmap(cm, annot=False, cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'confusion_matrix.png'))
    plt.close()
    
    plt.figure(figsize=(20, 20))
    sns.heatmap(cm_norm, annot=False, cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.title('Normalized Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'confusion_matrix_normalized.png'))
    plt.close()
    
    # ---------------------------------------------------------
    # 3. Per-Class Metrics
    # ---------------------------------------------------------
    per_class_list = []
    for i, cls in enumerate(class_names):
        m = report_dict[cls]
        per_class_list.append({
            'class': cls,
            'precision': m['precision'],
            'recall': m['recall'],
            'f1': m['f1-score'],
            'support': m['support']
        })
    df_per_class = pd.DataFrame(per_class_list).sort_values(by='f1')
    df_per_class.to_csv(os.path.join(EVALUATION_DIR, 'per_class_metrics.csv'), index=False)
    
    # ---------------------------------------------------------
    # 4. Crop-level & Healthy/Diseased Metrics
    # ---------------------------------------------------------
    crop_true = []
    crop_pred = []
    status_true = []
    status_pred = []
    
    for i in range(len(y_true)):
        t_meta = class_mapping[str(y_true[i])]
        p_meta = class_mapping[str(y_pred[i])]
        
        crop_true.append(t_meta['crop'])
        crop_pred.append(p_meta['crop'])
        
        status_true.append(t_meta['status'])
        status_pred.append(p_meta['status'])
        
    # Crop classification report
    crop_report = classification_report(crop_true, crop_pred, output_dict=True)
    pd.DataFrame(crop_report).transpose().to_csv(os.path.join(EVALUATION_DIR, 'crop_level_metrics.csv'))
    
    # Status classification report (Healthy vs Diseased)
    status_report = classification_report(status_true, status_pred, output_dict=True)
    pd.DataFrame(status_report).transpose().to_csv(os.path.join(EVALUATION_DIR, 'status_metrics.csv'))
    
    # ---------------------------------------------------------
    # 5. Misclassified Images
    # ---------------------------------------------------------
    # Save a small sample of misclassified images
    misclassified_idx = np.where(y_true != y_pred)[0]
    sample_size = min(20, len(misclassified_idx))
    sample_idx = np.random.choice(misclassified_idx, sample_size, replace=False)
    
    # Clear directory first
    for f in os.listdir(MISCLASSIFIED_DIR):
        os.remove(os.path.join(MISCLASSIFIED_DIR, f))
        
    for idx in sample_idx:
        t_cls = class_names[y_true[idx]]
        p_cls = class_names[y_pred[idx]]
        score = y_pred_probs[idx][y_pred[idx]]
        
        src_path = file_paths[idx]
        ext = os.path.splitext(src_path)[1]
        
        dest_name = f"True_{t_cls}__Pred_{p_cls}__Score_{score:.2f}{ext}".replace(" ", "_")
        shutil.copy2(src_path, os.path.join(MISCLASSIFIED_DIR, dest_name))
        
    # ---------------------------------------------------------
    # 6. Model Info & Environment
    # ---------------------------------------------------------
    model_size_bytes = os.path.getsize(model_path)
    trainable_count = np.sum([tf.keras.backend.count_params(w) for w in model.trainable_weights])
    non_trainable_count = np.sum([tf.keras.backend.count_params(w) for w in model.non_trainable_weights])
    
    model_info = {
        "model_file_size_mb": model_size_bytes / (1024 * 1024),
        "total_parameters": int(trainable_count + non_trainable_count),
        "trainable_parameters": int(trainable_count),
        "non_trainable_parameters": int(non_trainable_count),
        "macro_f1": report_dict['macro avg']['f1-score'],
        "weighted_f1": report_dict['weighted avg']['f1-score'],
        "accuracy": report_dict['accuracy']
    }
    with open(os.path.join(EVALUATION_DIR, 'model_info.json'), 'w') as f:
        json.dump(model_info, f, indent=4)
        
    env_info = {
        "tensorflow_version": tf.__version__,
        "evaluation_time_seconds": time.time() - start_time
    }
    with open(os.path.join(EVALUATION_DIR, 'training_environment.json'), 'w') as f:
        json.dump(env_info, f, indent=4)
        
    print("Evaluation complete. Results saved in ml/disease/evaluation/")

if __name__ == "__main__":
    main()
