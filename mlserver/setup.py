import os

MODEL_WEIGHT_PATH = os.getenv("MODEL_WEIGHT_PATH", "/app/data_storage/train_results/default_weight")

import os
import json
from pathlib import Path

def create_model_settings():
    model_settings = {
        "name": f"petcare-prediction-serving-{os.path.basename(MODEL_WEIGHT_PATH)}",
        "implementation": "mlserver_mlflow.MLflowRuntime",
        "parameters": {
            "uri": MODEL_WEIGHT_PATH,
            "version": "v1.0.0"
        }
    }
    
    # 설정 파일 저장
    with open("model-settings.json", "w") as f:
        json.dump(model_settings, f, indent=2)

if __name__ == "__main__":
    create_model_settings()