import os
import json
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from sklearn.utils.class_weight import compute_class_weight
from .config import METADATA_DIR, EVALUATION_DIR

def load_class_names():
    with open(os.path.join(METADATA_DIR, 'class_names.json'), 'r') as f:
        return json.load(f)

def verify_class_mapping(dataset_classes):
    """Verifies that the dataset class order matches the canonical order."""
    canonical_classes = load_class_names()
    if len(dataset_classes) != len(canonical_classes):
        raise ValueError("Class count mismatch!")
        
    for i, (d_cls, c_cls) in enumerate(zip(dataset_classes, canonical_classes)):
        if d_cls != c_cls:
            raise ValueError(f"Class mismatch at index {i}: dataset='{d_cls}', canonical='{c_cls}'")
    print("Class mapping verified successfully.")

def calculate_class_weights(dataset, num_classes):
    """Calculates class weights from a tf.data.Dataset."""
    print("Calculating class weights (this may take a minute)...")
    y_true = []
    for _, labels in dataset.unbatch():
        y_true.append(np.argmax(labels.numpy()))
        
    y_true = np.array(y_true)
    classes = np.arange(num_classes)
    
    weights = compute_class_weight('balanced', classes=classes, y=y_true)
    class_weights = {i: weight for i, weight in enumerate(weights)}
    
    # Save for reference
    with open(os.path.join(METADATA_DIR, 'class_weights.json'), 'w') as f:
        json.dump(class_weights, f, indent=4)
        
    return class_weights

def plot_training_history(history, experiment_name):
    """Plots and saves training and validation metrics."""
    os.makedirs(os.path.join(EVALUATION_DIR, 'plots'), exist_ok=True)
    
    # Accuracy plot
    plt.figure(figsize=(8, 6))
    plt.plot(history['accuracy'], label='Training Accuracy')
    plt.plot(history['val_accuracy'], label='Validation Accuracy')
    plt.title(f'{experiment_name} - Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.savefig(os.path.join(EVALUATION_DIR, 'plots', f'{experiment_name}_accuracy.png'))
    plt.close()
    
    # Loss plot
    plt.figure(figsize=(8, 6))
    plt.plot(history['loss'], label='Training Loss')
    plt.plot(history['val_loss'], label='Validation Loss')
    plt.title(f'{experiment_name} - Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.savefig(os.path.join(EVALUATION_DIR, 'plots', f'{experiment_name}_loss.png'))
    plt.close()

def save_experiment_results(experiment_name, results_dict):
    """Saves metrics to experiments.csv"""
    import pandas as pd
    csv_path = os.path.join(EVALUATION_DIR, 'experiments.csv')
    
    df = pd.DataFrame([results_dict])
    if os.path.exists(csv_path):
        existing_df = pd.read_csv(csv_path)
        # Drop previous run of same experiment if exists
        existing_df = existing_df[existing_df['experiment'] != experiment_name]
        df = pd.concat([existing_df, df], ignore_index=True)
        
    df.to_csv(csv_path, index=False)
