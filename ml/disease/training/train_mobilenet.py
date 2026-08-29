import os
import json
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D, Dropout, Dense
from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
import datetime
import argparse
from .config import *
from .utils import verify_class_mapping, calculate_class_weights, plot_training_history, save_experiment_results

def create_datasets():
    print("Loading datasets...")
    train_ds = tf.keras.utils.image_dataset_from_directory(
        TRAIN_DIR,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        label_mode='categorical',
        seed=RANDOM_STATE
    )
    
    val_ds = tf.keras.utils.image_dataset_from_directory(
        VAL_DIR,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        label_mode='categorical',
        seed=RANDOM_STATE
    )
    
    verify_class_mapping(train_ds.class_names)
    
    # Optimization
    AUTOTUNE = tf.data.AUTOTUNE
    # Cache is intentionally removed to avoid loading 54k images into RAM (reduces memory usage)
    train_ds = train_ds.prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)
    
    return train_ds, val_ds

def get_data_augmentation():
    return Sequential([
        tf.keras.layers.RandomFlip("horizontal"),
        tf.keras.layers.RandomRotation(0.1),
        tf.keras.layers.RandomZoom(0.1),
        tf.keras.layers.RandomTranslation(0.1, 0.1),
        tf.keras.layers.RandomContrast(0.1)
    ], name="data_augmentation")

def build_model(trainable_backbone=False, frozen_layers_count=None):
    inputs = tf.keras.Input(shape=INPUT_SHAPE)
    
    # Augmentation (only active during training)
    x = get_data_augmentation()(inputs)
    
    # Preprocessing
    x = tf.keras.applications.mobilenet_v2.preprocess_input(x)
    
    # Backbone
    base_model = MobileNetV2(input_shape=INPUT_SHAPE, include_top=False, weights='imagenet')
    
    if not trainable_backbone:
        base_model.trainable = False
    else:
        # Fine-tuning: unfreeze the top N layers
        base_model.trainable = True
        for layer in base_model.layers[:frozen_layers_count]:
            if not isinstance(layer, tf.keras.layers.BatchNormalization):
                layer.trainable = False
            
        # Ensure BatchNorm remains frozen to prevent statistics destruction
        for layer in base_model.layers:
            if isinstance(layer, tf.keras.layers.BatchNormalization):
                layer.trainable = False
                
    x = base_model(x, training=False if not trainable_backbone else None)
    
    # Head
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.2)(x)
    # Final Dense layer must use float32 for numerical stability even when using mixed precision
    outputs = Dense(NUM_CLASSES, activation='softmax', dtype='float32')(x)
    
    model = tf.keras.Model(inputs, outputs)
    return model, base_model

def get_callbacks(model_name):
    checkpoint_path = os.path.join(ARTIFACTS_DIR, f"{model_name}.keras")
    return [
        ModelCheckpoint(checkpoint_path, monitor='val_accuracy', save_best_only=True, verbose=1),
        EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True, verbose=1),
        ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=2, min_lr=1e-6, verbose=1)
    ]

def main():
    parser = argparse.ArgumentParser(description="Train MobileNetV2 for Plant Disease Detection")
    parser.add_argument("--smoke-test", action="store_true", help="Run a quick smoke test with 1 epoch and 2 steps")
    args = parser.parse_args()
    
    is_smoke_test = args.smoke_test
    
    epochs_stage1 = 1 if is_smoke_test else INITIAL_EPOCHS
    epochs_stage3 = 1 if is_smoke_test else FINE_TUNE_EPOCHS
    steps_per_epoch = 2 if is_smoke_test else None
    validation_steps = 2 if is_smoke_test else None

    # Set mixed precision if GPU allows
    try:
        policy = tf.keras.mixed_precision.Policy('mixed_float16')
        tf.keras.mixed_precision.set_global_policy(policy)
        print("Mixed precision enabled. (Helps reduce GPU memory usage)")
    except Exception as e:
        print("Could not enable mixed precision:", e)
        
    train_ds, val_ds = create_datasets()
    
    # ---------------------------------------------------------
    # STAGE 1: Baseline (No Class Weights)
    # ---------------------------------------------------------
    print("\n--- STAGE 1: Baseline Training ---")
    model_baseline, _ = build_model(trainable_backbone=False)
    model_baseline.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=INITIAL_LR),
        loss=tf.keras.losses.CategoricalCrossentropy(),
        metrics=['accuracy']
    )
    
    history_baseline = model_baseline.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs_stage1,
        steps_per_epoch=steps_per_epoch,
        validation_steps=validation_steps,
        callbacks=get_callbacks('exp_baseline')
    )
    plot_training_history(history_baseline.history, 'exp_baseline')
    save_experiment_results('exp_baseline', {
        'experiment': 'exp_baseline',
        'backbone': 'MobileNetV2',
        'class_weights': False,
        'frozen_layers': 'All',
        'learning_rate': INITIAL_LR,
        'epochs': len(history_baseline.history['loss']),
        'validation_accuracy': max(history_baseline.history['val_accuracy']),
        'validation_loss': min(history_baseline.history['val_loss']),
        'notes': 'Stage 1 baseline'
    })
    
    # ---------------------------------------------------------
    # STAGE 2: Class-Weighted Training
    # ---------------------------------------------------------
    print("\n--- STAGE 2: Class-Weighted Training ---")
    class_weights = calculate_class_weights(train_ds, NUM_CLASSES)
    
    # Keep the base_model reference so we can fine-tune it directly in Stage 3
    model_cw, base_model = build_model(trainable_backbone=False)
    model_cw.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=INITIAL_LR),
        loss=tf.keras.losses.CategoricalCrossentropy(),
        metrics=['accuracy']
    )
    
    history_cw = model_cw.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs_stage1,
        steps_per_epoch=steps_per_epoch,
        validation_steps=validation_steps,
        class_weight=class_weights,
        callbacks=get_callbacks('exp_class_weight')
    )
    plot_training_history(history_cw.history, 'exp_class_weight')
    save_experiment_results('exp_class_weight', {
        'experiment': 'exp_class_weight',
        'backbone': 'MobileNetV2',
        'class_weights': True,
        'frozen_layers': 'All',
        'learning_rate': INITIAL_LR,
        'epochs': len(history_cw.history['loss']),
        'validation_accuracy': max(history_cw.history['val_accuracy']),
        'validation_loss': min(history_cw.history['val_loss']),
        'notes': 'Stage 2 class weights'
    })
    
    # ---------------------------------------------------------
    # STAGE 3: Fine-Tuning
    # ---------------------------------------------------------
    print("\n--- STAGE 3: Fine-Tuning ---")
    # Fine-tune the base_model directly.
    # Unfreeze the last FINE_TUNE_LAST_N_LAYERS non-BatchNorm layers.
    base_model.trainable = True
    
    for layer in base_model.layers[:-FINE_TUNE_LAST_N_LAYERS]:
        if not isinstance(layer, tf.keras.layers.BatchNormalization):
            layer.trainable = False

    # Ensure all BatchNormalization layers remain frozen to prevent destroying learned statistics
    for layer in base_model.layers:
        if isinstance(layer, tf.keras.layers.BatchNormalization):
            layer.trainable = False
    
    # Recompile after changing trainable state
    model_cw.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=FINE_TUNE_LR),
        loss=tf.keras.losses.CategoricalCrossentropy(),
        metrics=['accuracy']
    )
    
    history_ft = model_cw.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs_stage3,
        steps_per_epoch=steps_per_epoch,
        validation_steps=validation_steps,
        class_weight=class_weights,
        callbacks=get_callbacks('exp_finetuned')
    )
    plot_training_history(history_ft.history, 'exp_finetuned')
    save_experiment_results('exp_finetuned', {
        'experiment': 'exp_finetuned',
        'backbone': 'MobileNetV2',
        'class_weights': True,
        'frozen_layers': f'All but last {FINE_TUNE_LAST_N_LAYERS}',
        'learning_rate': FINE_TUNE_LR,
        'epochs': len(history_ft.history['loss']),
        'validation_accuracy': max(history_ft.history['val_accuracy']),
        'validation_loss': min(history_ft.history['val_loss']),
        'notes': 'Stage 3 fine-tuned'
    })
    
    if is_smoke_test:
        print("\nSmoke test completed successfully!")
    else:
        print("\nAll training stages completed!")

if __name__ == "__main__":
    main()
