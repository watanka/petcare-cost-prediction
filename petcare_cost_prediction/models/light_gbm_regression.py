import os
from typing import Optional, Dict, Union, List

import lightgbm as lgb
from lightgbm import LGBMRegressor
import numpy as np
import pandas as pd

from petcare_cost_prediction.models.base_model import BasePetCareCostPredictionModel



LGB_REGRESSION_DEFAULT_PARAMS = {
    "task": "train",
    "boosting": "gbdt",
    "objective": "regression",
    "num_leaves": 3,
    "learning_rate": 0.05,
    "early_stopping_rounds" : 200,
    "feature_fraction": 0.5,
    "max_depth": -1,
    "num_iterations": 1000000,
    "num_threads": 0,
    "seed": 1234,
    'verbose_eval': 1000
}


class LightGBMRegressionModel(BasePetCareCostPredictionModel):
    
    def __init__(self, 
                 params: Dict = LGB_REGRESSION_DEFAULT_PARAMS,
                 eval_metrics: Union[str, List[str]] = 'mse',
                 ):
        self.name = "light_gbm_regression"
        self.params = params
        self.eval_metrics = eval_metrics

        self.model: LGBMRegressor = None
        self.reset_model(params=self.params)
        self.column_length: int = 0


    def reset_model(
        self,
        params: Optional[Dict] = None,
    ):
        if params is not None:
            self.params = params
        
        self.model = LGBMRegressor(**self.params)
        
    def train(
        self,
        x_train: Union[np.ndarray, pd.DataFrame],
        y_train: Union[np.ndarray, pd.DataFrame],
        x_test: Optional[Union[np.ndarray, pd.DataFrame]] = None,
        y_test: Optional[Union[np.ndarray, pd.DataFrame]] = None,
    ):
        eval_set = [(x_train, y_train)]
        if x_test is not None and y_test is not None:
            eval_set.append((x_test, y_test))
        self.model.fit(
            X=x_train,
            y=y_train,
            eval_set=eval_set,
            eval_metric=self.eval_metrics,
        )
        
    def predict(
        self,
        x: Union[pd.DataFrame, np.array],
    ) -> Union[np.ndarray, pd.DataFrame]:
        
        prediction = self.model.predict(x)
        return prediction
    
    def save(self, file_path: str) -> str:
        file, ext = os.path.splitext(file_path)
        if ext != ".txt":
            file_path = f"{file}.txt"
        self.model.booster_.save_model(file_path)
        return file_path
    
    def load(
        self,
        file_path: str
    ):
        self.model = lgb.Booster(model_file = file_path)