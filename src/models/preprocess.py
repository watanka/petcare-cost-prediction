from abc import ABC, abstractmethod
from typing import Union
import pandas as pd
import datetime
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, MinMaxScaler, OneHotEncoder


class AgeCalculator(BaseEstimator, TransformerMixin):
    ## age 계산 후, minmax scaling적용하기
    def __init__(self):
        self.scaler = MinMaxScaler()
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X['age'] = X.apply(lambda row: self.calculate_age(row['birth'], row['created_at']), axis = 1)
        age_values = np.array(X['age']).reshape(-1, 1)
        scaled_age = self.scaler.fit_transform(age_values)
        
        X['age'] = scaled_age.flatten()
        
        return X.drop(columns=['birth', 'created_at'])

    def calculate_age(self, birth: datetime.date, created_at: pd.Timestamp) -> int:
        created_at = created_at.to_pydatetime().date()
        age = (created_at - birth).days
        return age

class BasePreprocessPipeline(ABC, BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    @abstractmethod
    def fit(
        self,
        x: pd.DataFrame,
        y=None,
    ):
        raise NotImplementedError

    @abstractmethod
    def transform(
        self,
        x: pd.DataFrame,
    ) -> np.ndarray:
        raise NotImplementedError

    @abstractmethod
    def fit_transform(
        self,
        x: pd.DataFrame,
        y=None,
    ) -> np.ndarray:
        raise NotImplementedError

    @abstractmethod
    def dump_pipeline(
        self,
        file_path: str,
    ):
        raise NotImplementedError

    @abstractmethod
    def load_pipeline(
        self,
        file_path: str,
    ):
        raise NotImplementedError
    
    
class DataPreprocessPipeline:
    def __init__(self):
        self.pipeline: Union[Pipeline, ColumnTransformer] = None
        
        
        
    def define_pipeline(self):
        self.pipeline = ColumnTransformer(
            transformers = [
                # ('simple_imputer', SimpleImputer(missing_values=np.nan, strategy = 'constant', fill_value = None), ['pet_breed_id', 'birth', 'gender', 'neuter_yn', 'weight_kg']),
                ('one_hot_encoder', OneHotEncoder(), ['gender', 'neuter_yn']),
                ('age_calculator', AgeCalculator(), ['birth', 'created_at']),
                ('min_max_scaler', MinMaxScaler(), ['weight_kg']),
            ]
        )
        
    def preprocess(self, x) -> pd.DataFrame:
        self.fit(x)
        return pd.DataFrame(self.pipeline.transform(x))
    
    def fit(self, x: pd.DataFrame, y = None):
        self.pipeline.fit(x)
        return self
    
    def transform(self, x):
        ## NOT USING FOR NOW
        return x