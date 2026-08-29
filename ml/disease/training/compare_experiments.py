import os
import pandas as pd
import shutil
from .config import EVALUATION_DIR, ARTIFACTS_DIR

def main():
    csv_path = os.path.join(EVALUATION_DIR, 'experiments.csv')
    if not os.path.exists(csv_path):
        print("No experiments found to compare.")
        return
        
    df = pd.read_csv(csv_path)
    print("--- Experiment Results ---")
    print(df[['experiment', 'validation_accuracy', 'validation_loss']])
    
    # Sort by validation accuracy descending, then loss ascending
    df_sorted = df.sort_values(by=['validation_accuracy', 'validation_loss'], ascending=[False, True])
    best_experiment = df_sorted.iloc[0]['experiment']
    
    print(f"\nBest model selected based on Validation Accuracy: {best_experiment}")
    
    # Copy best model to final path
    best_model_src = os.path.join(ARTIFACTS_DIR, f"{best_experiment}.keras")
    final_model_dst = os.path.join(ARTIFACTS_DIR, "plant_disease_model.keras")
    
    if os.path.exists(best_model_src):
        shutil.copy2(best_model_src, final_model_dst)
        print(f"Saved best model to {final_model_dst}")
        
        # Save model metadata
        import json
        metadata = {
            "model_name": "MobileNetV2",
            "model_version": "1.0.0",
            "input_size": [224, 224, 3],
            "num_classes": 38,
            "preprocessing": "mobilenet_v2.preprocess_input",
            "random_state": 42,
            "selected_experiment": best_experiment,
            "validation_accuracy": float(df_sorted.iloc[0]['validation_accuracy'])
        }
        with open(os.path.join(ARTIFACTS_DIR, 'model_metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=4)
    else:
        print(f"Error: Could not find model artifact {best_model_src}")

if __name__ == "__main__":
    main()
