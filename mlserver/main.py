import mlflow
import os

MODEL_WEIGHT_PATH = os.getenv("MODEL_WEIGHT_PATH")

model = mlflow.lightgbm.load_model(MODEL_WEIGHT_PATH)

model.serve(port = 8080, enable_mlserver=True)