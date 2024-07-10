import numpy as np
import pandas as pd
from typing import Union
import os
from src.middleware.logger import configure_logger

logger = configure_logger(__name__)


class DataRegister:
    def __init__(self):
        pass

    def register(
        self, predictions: Union[pd.DataFrame, np.ndarray], prediction_file_path: str
    ):
        file, ext = os.path.splitext(prediction_file_path)
        if ext != ".csv":
            prediction_file_path = f"{file}.csv"

        logger.info(f"save prediction as csv: {prediction_file_path}")
        predictions.to_csv(prediction_file_path, index=False)
        return prediction_file_path
