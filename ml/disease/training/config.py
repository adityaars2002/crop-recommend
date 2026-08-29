import os

# Base Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'disease', 'processed')
TRAIN_DIR = os.path.join(DATA_DIR, 'train')
VAL_DIR = os.path.join(DATA_DIR, 'val')
TEST_DIR = os.path.join(DATA_DIR, 'test')

METADATA_DIR = os.path.join(PROJECT_ROOT, 'ml', 'disease', 'metadata')
ARTIFACTS_DIR = os.path.join(PROJECT_ROOT, 'ml', 'disease', 'artifacts')
EVALUATION_DIR = os.path.join(PROJECT_ROOT, 'ml', 'disease', 'evaluation')

# Model Parameters
IMAGE_SIZE = (224, 224)
INPUT_SHAPE = (224, 224, 3)
BATCH_SIZE = 16  # Reduced to 16 for RTX 2050 (4GB VRAM) to prevent OOM errors during backprop/augmentation
NUM_CLASSES = 38
RANDOM_STATE = 42

# Training Parameters
INITIAL_EPOCHS = 15
INITIAL_LR = 1e-3

FINE_TUNE_EPOCHS = 10
FINE_TUNE_LR = 1e-5
FINE_TUNE_LAST_N_LAYERS = 30  # Number of top layers to unfreeze for fine-tuning

# Inference
MIN_PREDICTION_SCORE = 0.5
