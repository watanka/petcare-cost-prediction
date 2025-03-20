from typing import Union, Dict, List, Optional, Tuple
import os
from joblib import dump, load
import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, StandardScaler, RobustScaler
from sklearn.model_selection import train_test_split as sk_train_test_split
from src.dataset.schema import XY
from src.logger import setup_logger

logger = setup_logger(__name__)

class DataPreprocessPipeline(BaseEstimator, TransformerMixin):
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.pipeline = None
        logger.info("전처리 파이프라인 초기화")
    
    def define_pipeline(self):
        transformers = []
        column_configs = self.config.get("columns", {})
        drop_columns = self.config.get("drop_columns", [])
        
        for column, settings in column_configs.items():
            if column in drop_columns:
                continue
                
            column_type = settings.get("type", "numeric")
            handling = settings.get("handling", "none")
            missing_value = settings.get("missing_value", "mean" if column_type == "numeric" else "drop")
            
            steps = []
            
            # 결측치 처리
            if missing_value in ["mean", "median", "zero"]:
                imputer = SimpleImputer(strategy=missing_value)
            elif missing_value == "mode":
                imputer = SimpleImputer(strategy="most_frequent")
            elif missing_value == "drop":
                imputer = SimpleImputer(strategy="drop")
            else:
                imputer = None
                
            if imputer:
                steps.append(("impute", imputer))
            
            # 전처리
            if column_type == "numeric":
                if handling == "standard_scale":
                    steps.append(("scale", StandardScaler()))
                elif handling == "minmax_scale":
                    steps.append(("scale", MinMaxScaler()))
                elif handling == "log_transform":
                    steps.append(("log", lambda x: np.log1p(x)))
            elif column_type == "categorical":
                if handling == "one_hot":
                    steps.append(("encode", OneHotEncoder(sparse_output=False, handle_unknown='ignore')))
                elif handling == "label":
                    steps.append(("encode", lambda x: pd.factorize(x)[0]))
            
            if steps:
                pipeline = Pipeline(steps)
                transformers.append((f"transform_{column}", pipeline, [column]))
        
        self.pipeline = ColumnTransformer(
            transformers=transformers,
            remainder="drop"
        )
    
    def fit(self, x: pd.DataFrame, y=None):
        logger.info("전처리 파이프라인 학습 시작")
        if self.pipeline is None:
            self.define_pipeline()
        self.pipeline.fit(x)
        logger.info("전처리 파이프라인 학습 완료")
        return self
    
    def transform(self, x: pd.DataFrame) -> np.ndarray:
        logger.info("데이터 변환 시작")
        if self.pipeline is None:
            raise ValueError("파이프라인이 학습되지 않았습니다.")
        result = self.pipeline.transform(x)
        logger.info("데이터 변환 완료")
        return result

    def fit_transform(self, x: pd.DataFrame, y=None) -> np.ndarray:
        return self.fit(x).transform(x)

    def dump_pipeline(self, file_path: str) -> str:
        logger.info(f"파이프라인 저장: {file_path}")
        file, ext = os.path.splitext(file_path)
        if ext != ".pkl":
            file_path = f"{file}.pkl"
        dump({"pipeline": self.pipeline, "config": self.config}, file_path)
        return file_path

    def load_pipeline(self, file_path: str):
        logger.info(f"파이프라인 로드: {file_path}")
        saved_dict = load(file_path)
        self.pipeline = saved_dict["pipeline"]
        self.config = saved_dict["config"]

    def get_feature_names(self) -> list:
        if self.pipeline is None:
            raise ValueError("파이프라인이 학습되지 않았습니다.")
        return self.pipeline.get_feature_names_out().tolist()

def split_train_test(
    raw_df: pd.DataFrame,
    test_split_ratio: float,
    data_preprocess_pipeline: DataPreprocessPipeline,
) -> Tuple[XY, XY]:
    """데이터를 학습/테스트 세트로 분할하고 전처리를 수행합니다."""
    x = raw_df.drop(columns=["price"])
    y = raw_df[["price"]].astype(np.float64)

    x_train, x_test, y_train, y_test = sk_train_test_split(
        x, y, test_size=test_split_ratio, random_state=42
    )
    
    preprocessed_train_x = data_preprocess_pipeline.fit_transform(x_train)
    preprocessed_test_x = data_preprocess_pipeline.transform(x_test)
    
    return XY(x=preprocessed_train_x, y=y_train), XY(x=preprocessed_test_x, y=y_test)



