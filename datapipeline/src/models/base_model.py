from typing import Optional, Dict, Union
import numpy as np
import pandas as pd

from abc import ABC, abstractmethod

# Interface


class BasePetCareCostPredictionModel(ABC):
    def __init__(self):
        self.name: str = "pet_care_cost_prediction"

        self.model = None

    @abstractmethod
    def reset_model(self, params: Optional[Dict] = None):
        raise NotImplementedError

    @abstractmethod
    def train(
        self,
        x_train: Union[np.ndarray, pd.DataFrame],
        y_train: Union[np.ndarray, pd.DataFrame],
        x_test: Optional[Union[np.ndarray, pd.DataFrame]] = None,
        y_test: Optional[Union[np.ndarray, pd.DataFrame]] = None,
    ):
        raise NotImplementedError

    @abstractmethod
    def predict(
        self,
        x: Union[np.ndarray, pd.DataFrame],
    ) -> Union[np.ndarray, pd.DataFrame]:
        raise NotImplementedError

    @abstractmethod
    def save(self, file_path: str):
        raise NotImplementedError

    @abstractmethod
    def load(self, file_path: str):
        raise NotImplementedError
