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
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, StandardScaler

from src.logger import setup_logger


logger = setup_logger(__name__)



from datetime import date
import pandas as pd
import numpy as np

from typing import List, Tuple
from sklearn.model_selection import train_test_split as sk_train_test_split

from src.dataset.schema import XY
from src.logger import setup_logger


logger = setup_logger(__name__)





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
    def fit(self, x: pd.DataFrame, y=None):
        raise NotImplementedError

    @abstractmethod
    def transform(self, x: pd.DataFrame) -> np.ndarray:
        raise NotImplementedError

    @abstractmethod
    def fit_transform(self, x: pd.DataFrame, y=None) -> np.ndarray:
        raise NotImplementedError

    @abstractmethod
    def dump_pipeline(self, file_path: str):
        raise NotImplementedError

    @abstractmethod
    def load_pipeline(self, file_path: str):
        raise NotImplementedError


class DataPreprocessPipeline(BasePreprocessPipeline):
    def __init__(self, config=None):
        self.pipeline: Union[Pipeline, ColumnTransformer] = None
        self.config = config or {}
        logger.info("전처리 파이프라인 초기화")

    def define_pipeline(self):
        transformers = []
        
        # config에서 각 컬럼별 설정을 가져옴
        column_configs = self.config.get("columns", {})
        logger.info(f"컬럼별 전처리 설정: {column_configs}")
        
        for column, settings in column_configs.items():
            column_type = settings.get("type", "numeric")  # 기본값은 numeric
            steps = []
            
            # 결측치 처리
            missing_strategy = settings.get("missing_value", "mean" if column_type == "numeric" else "constant")
            if column_type == "numeric":
                steps.append(("imputer", SimpleImputer(
                    strategy=missing_strategy
                )))
            else:  # categorical
                steps.append(("imputer", SimpleImputer(
                    strategy=missing_strategy,
                    fill_value="unknown"
                )))
            
            # 스케일링/인코딩
            handling = settings.get("handling", None)
            if handling:
                if handling == "standard_scale":
                    steps.append(("scaler", StandardScaler()))
                elif handling == "minmax_scale":
                    steps.append(("scaler", MinMaxScaler()))
                elif handling == "one_hot":
                    steps.append(("encoder", OneHotEncoder(
                        handle_unknown="ignore",
                        sparse_output=False
                    )))
            
            # 컬럼별 파이프라인 생성
            if steps:
                pipeline = Pipeline(steps)
                transformers.append((f"transform_{column}", pipeline, [column]))
                logger.info(f"컬럼 '{column}' 파이프라인 구성: {steps}")
        
        # 전체 파이프라인 구성
        self.pipeline = ColumnTransformer(
            transformers=transformers,
            remainder="drop"  # 설정되지 않은 컬럼은 제외
        )
        
        logger.info("전처리 파이프라인 구성 완료")

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
        
        # 파이프라인과 함께 설정도 저장
        save_dict = {
            "pipeline": self.pipeline,
            "config": self.config
        }
        dump(save_dict, file_path)
        return file_path

    def load_pipeline(self, file_path: str):
        logger.info(f"파이프라인 로드: {file_path}")
        saved_dict = load(file_path)
        self.pipeline = saved_dict["pipeline"]
        self.config = saved_dict["config"]

    def get_feature_names(self) -> list:
        """변환된 특성의 이름을 반환합니다."""
        if self.pipeline is None:
            raise ValueError("파이프라인이 학습되지 않았습니다.")
            
        return self.pipeline.get_feature_names_out().tolist()



def split_train_test(
        raw_df: pd.DataFrame,
        test_split_ratio: float,
        data_preprocess_pipeline: DataPreprocessPipeline,
    ) -> Tuple[XY, XY]:
        """
        데이터를 학습/테스트 세트로 분할하고 전처리를 수행합니다.
        
        Args:
            raw_df (pd.DataFrame): 원본 데이터
            test_split_ratio (float): 테스트 세트 비율
            data_preprocess_pipeline (DataPreprocessPipeline): 전처리 파이프라인
            
        Returns:
            Tuple[XY, XY]: (학습 데이터, 테스트 데이터) 튜플
        """
        x = raw_df.drop(columns=["price"])
        y = raw_df[["price"]].astype(np.float64)

        x_train, x_test, y_train, y_test = sk_train_test_split(
            x, y, test_size=test_split_ratio, random_state=42
        )
        
        preprocessed_train_x = data_preprocess_pipeline.fit_transform(x_train)
        preprocessed_test_x = data_preprocess_pipeline.transform(x_test)
        
        # TODO: test_size config로 옮기기

        # x, y 나누기
        return XY(x=preprocessed_train_x, y=y_train), XY(x=preprocessed_test_x, y=y_test)



