from abc import ABC, abstractmethod
from typing import Union

import os
from joblib import dump, load
import pandas as pd
import datetime
import numpy as np

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder

from logger import configure_logger

logger = configure_logger(__name__)

def calculate_age(birth: datetime.date, created_at: pd.Timestamp) -> int:
    
    if isinstance(created_at, pd.Timestamp):
        created_at = created_at.to_pydatetime().date()
    elif isinstance(created_at, str):
        created_at = datetime.datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S").date()
        
    if isinstance(birth, pd.Timestamp):
        birth = birth.to_pydatetime().date()
    elif isinstance(birth, str):
        birth = datetime.datetime.strptime(birth, "%Y-%m-%d").date()
    
    age = (created_at - birth).days
    return age


class MinMaxScalerReverse:
    def __init__(self, minval, maxval):
        self.minval = minval
        self.maxval = maxval

    def inverse_transform(self, x):
        return x * (self.maxval - self.minval) + self.minval

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


class DataPreprocessPipeline(BasePreprocessPipeline):
    def __init__(self):
        self.pipeline: Union[Pipeline, ColumnTransformer] = None

        self.categorical_columns = ["pet_breed_id", "gender", "neuter_yn"]
        self.numerical_columns = ["age", "weight"]

    def define_pipeline(self):
        self.categorical_pipeline = Pipeline(
            [
                (
                    "simple_imputer",
                    SimpleImputer(
                        missing_values=np.nan, strategy="constant", fill_value=None
                    ),
                ),
                ("one_hot_encoder", OneHotEncoder(handle_unknown="ignore")),
            ]
        )

        self.numerical_pipeline = Pipeline(
            [
                (
                    "simple_imputer",
                    SimpleImputer(
                        missing_values=np.nan,
                        strategy="constant",
                        fill_value=None,
                        add_indicator=True,
                    ),
                ),
                ("scaler", MinMaxScaler()),
            ]
        )

        self.pipeline = ColumnTransformer(
            transformers=[
                ("categorical", self.categorical_pipeline, self.categorical_columns),
                ("min_max_scaler", self.numerical_pipeline, self.numerical_columns),
            ]
        )


    def preprocess(self, x, breeds) -> pd.DataFrame:
        x['pet_breed_id'] = x['pet_breed_id'].apply(lambda x: x if x in breeds else 0)
        
        if 'age' not in x.columns:
            x["age"] = x.apply(
                lambda row: calculate_age(row["birth"], row["created_at"]), axis=1
            )
            x.drop(columns=["birth", "created_at"], inplace=True)

        

    
        # TODO: age와 weight에 대한 정규화 문제 남아있음.
        self.age_max, self.age_min = x["age"].max(), x["age"].min()
        self.weight_max, self.weight_min = x["weight_kg"].max(), x["weight_kg"].min()


        return pd.DataFrame(x)


    def fit(self, x: pd.DataFrame, y=None):
        self.pipeline.fit(x)
        return self

    def transform(self, x):
        return self.pipeline.transform(x)
        

    def fit_transform(self, x):
        return self.pipeline.fit_transform(x)

    def dump_pipeline(self, file_path: str) -> str:
        file, ext = os.path.splitext(file_path)
        if ext != ".pkl":
            file_path = f"{file}.pkl"
        dump(self.pipeline, file_path)
        return file_path

    def load_pipeline(self, file_path: str):
        
        self.pipeline = load(file_path)

    def inverse_transform(self, df):
        pass
        # df["gender"] = (
        #     df[self.gender_categories].idxmax(axis=1).apply(lambda x: x.split("_")[-1])
        # )
        # df["neuter_yn"] = (
        #     df[self.neutralized_categories]
        #     .idxmax(axis=1)
        #     .apply(lambda x: x.split("_")[-1])
        # )
        # df["pet_breed_id"] = (
        #     df[self.pet_breed_categories]
        #     .idxmax(axis=1)
        #     .apply(lambda x: x.split("_")[-1])
        # )

        # # numerical 역변환
        # weightScaler = MinMaxScalerReverse(
        #     minval=self.weight_min, maxval=self.weight_max
        # )
        # ageScaler = MinMaxScalerReverse(minval=self.age_min, maxval=self.age_max)
        # df["weight_kg"] = df["min_max_scaler__weight_kg"].apply(
        #     lambda x: weightScaler.inverse_transform(x)
        # )
        # df["age"] = df["min_max_scaler__age"].apply(
        #     lambda x: ageScaler.inverse_transform(x)
        # )

        # # df['weight_kg', 'age'] = self.numerical_pipeline.inverse_transform(df[['min_max_scaler__weight_kg', 'min_max_scaler__age']])

        # df.drop(self.pet_breed_categories, inplace=True, axis=1)
        # df.drop(self.gender_categories, inplace=True, axis=1)
        # df.drop(self.neutralized_categories, inplace=True, axis=1)
        # df.drop(
        #     ["min_max_scaler__weight_kg", "min_max_scaler__age"], inplace=True, axis=1
        # )

        # return df
