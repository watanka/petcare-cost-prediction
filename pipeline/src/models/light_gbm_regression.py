import os
from typing import Optional, Dict, Union, List

import lightgbm as lgb
from lightgbm import LGBMRegressor
import numpy as np
import pandas as pd

import mlflow
from mlserver.utils import get_model_uri

from src.models.base_model import BasePetCareCostPredictionModel
from src.logger import get_logger

logger = get_logger("light_gbm_regression")

class LightGBMRegressionModel(BasePetCareCostPredictionModel):

    def __init__(
        self,
        params: Optional[Dict] = None,
        eval_metrics: Union[str, List[str]] = "mse",
    ):
        self.model_name = "light_gbm_regression"
        self.params = self._get_default_params()
        if params:
            logger.info("사용자 정의 파라미터를 적용합니다.")
            self.params.update(params)
        self.eval_metrics = eval_metrics

        logger.debug(f"모델 파라미터: {self.params}")
        logger.debug(f"평가 지표: {self.eval_metrics}")

        self.model: LGBMRegressor = None
        self.reset_model(params=self.params)
        self.column_length: int = 0

    def _get_default_params(self) -> Dict:
        """기본 파라미터를 반환합니다."""
        return {
            "task": "train",
            "boosting": "gbdt",
            "objective": "regression",
            "num_leaves": 3,
            "learning_rate": 0.05,
            "early_stopping_rounds": 200,
            "feature_fraction": 0.5,
            "max_depth": -1,
            "num_iterations": 1000000,
            "num_threads": 0,
            "seed": 1234,
            "verbose_eval": 1000,
        }

    def reset_model(
        self,
        params: Optional[Dict] = None,
    ):
        if params is not None:
            self.params = params
            logger.info("모델 파라미터를 재설정합니다.")
            logger.debug(f"새로운 파라미터: {params}")

        self.model = LGBMRegressor(**self.params)

    def train(
        self,
        x_train: Union[np.ndarray, pd.DataFrame],
        y_train: Union[np.ndarray, pd.DataFrame],
        x_test: Optional[Union[np.ndarray, pd.DataFrame]] = None,
        y_test: Optional[Union[np.ndarray, pd.DataFrame]] = None,
    ):
        logger.info("모델 학습을 시작합니다.")
        eval_set = [(x_train, y_train)]
        if x_test is not None and y_test is not None:
            eval_set.append((x_test, y_test))
            logger.info("검증 데이터셋이 포함되었습니다.")

        try:
            self.model.train(
                X=x_train,
                y=y_train,
                eval_set=eval_set,
                eval_metric=self.eval_metrics,
            )
            logger.info("모델 학습이 완료되었습니다.")
        except Exception as e:
            logger.error(f"모델 학습 중 오류가 발생했습니다: {str(e)}", exc_info=True)
            raise

    def predict(
        self,
        x: Union[pd.DataFrame, np.array],
    ) -> Union[np.ndarray, pd.DataFrame]:
        logger.info("예측을 시작합니다.")
        try:
            prediction = self.model.predict(x)
            logger.info("예측이 완료되었습니다.")
            return prediction
        except Exception as e:
            logger.error(f"예측 중 오류가 발생했습니다: {str(e)}", exc_info=True)
            raise

    def save(self, file_path: str) -> str:
        logger.info(f"모델을 저장합니다: {file_path}")
        try:
            self.model.save(file_path)
            logger.info("모델 저장이 완료되었습니다.")
            return file_path
        except Exception as e:
            logger.error(f"모델 저장 중 오류가 발생했습니다: {str(e)}", exc_info=True)
            raise

    def load(self, file_path: str):
        logger.info(f"모델을 로드합니다: {file_path}")
        try:
            self.model = lgb.Booster(model_file=file_path)
            logger.info("모델 로드가 완료되었습니다.")
        except Exception as e:
            logger.error(f"모델 로드 중 오류가 발생했습니다: {str(e)}", exc_info=True)
            raise


class LightGBMRegressionModelServing(BasePetCareCostPredictionModel):

    def __init__(
        self,
        params: Optional[Dict] = None,
        eval_metrics: Union[str, List[str]] = "mse",
    ):
        self.model_name = "light_gbm_regression_serving"
        self.params = self._get_default_params()
        if params:
            logger.info("서빙용 모델에 사용자 정의 파라미터를 적용합니다.")
            self.params.update(params)
        self.eval_metrics = eval_metrics

        logger.debug(f"서빙용 모델 파라미터: {self.params}")
        logger.debug(f"서빙용 모델 평가 지표: {self.eval_metrics}")

        self.model: LGBMRegressor = None
        self.column_length: int = 0

    def set_eval_metrics(self, eval_metrics: Union[str, List[str]]):
        if isinstance(eval_metrics, str):
            self.eval_metrics = [eval_metrics]
        elif isinstance(eval_metrics, list):
            self.eval_metrics = eval_metrics
        else:
            raise ValueError(f"eval_metrics must be a string or a list of strings, but got {type(eval_metrics)}")

    def _get_default_params(self) -> Dict:
        """기본 파라미터를 반환합니다."""
        return {
            "task": "train",
            "boosting": "gbdt",
            "objective": "regression",
            "num_leaves": 3,
            "learning_rate": 0.05,
            "early_stopping_rounds": 200,
            "feature_fraction": 0.5,
            "max_depth": -1,
            "num_iterations": 1000000,
            "num_threads": 0,
            "seed": 1234,
            "verbose_eval": 1000,
        }

    def reset_model(
        self,
        params: Optional[Dict] = None,
    ):
        if params is not None:
            self.params = params
            logger.info("서빙용 모델 파라미터를 재설정합니다.")
            logger.debug(f"새로운 파라미터: {params}")

        self.model = LGBMRegressor(**self.params)

    def train(
        self,
        x_train: Union[np.ndarray, pd.DataFrame],
        y_train: Union[np.ndarray, pd.DataFrame],
        x_test: Optional[Union[np.ndarray, pd.DataFrame]] = None,
        y_test: Optional[Union[np.ndarray, pd.DataFrame]] = None,
    ):
        logger.info("서빙용 모델 학습을 시작합니다.")
        eval_set = [(x_train, y_train)]
        if x_test is not None and y_test is not None:
            eval_set.append((x_test, y_test))
            logger.info("검증 데이터셋이 포함되었습니다.")

        try:
            self.model.fit(
                X=x_train,
                y=y_train,
                eval_set=eval_set,
                eval_metric=self.eval_metrics,
            )
            logger.info("서빙용 모델 학습이 완료되었습니다.")
        except Exception as e:
            logger.error(f"서빙용 모델 학습 중 오류가 발생했습니다: {str(e)}", exc_info=True)
            raise

    def predict(
        self,
        x: Union[pd.DataFrame, np.array],
    ) -> Union[np.ndarray, pd.DataFrame]:
        logger.info("서빙용 모델 예측을 시작합니다.")
        try:
            prediction = self.model.predict(x)
            logger.info("서빙용 모델 예측이 완료되었습니다.")
            return prediction
        except Exception as e:
            logger.error(f"서빙용 모델 예측 중 오류가 발생했습니다: {str(e)}", exc_info=True)
            raise

    def save(self, file: str) -> str:
        logger.info(f"서빙용 모델을 저장합니다: {file}")
        try:
            file_path, ext = os.path.splitext(file)
            mlflow.lightgbm.save_model(self.model, file_path)
            logger.info("서빙용 모델 저장이 완료되었습니다.")
            return file_path
        except Exception as e:
            logger.error(f"서빙용 모델 저장 중 오류가 발생했습니다: {str(e)}", exc_info=True)
            raise

    async def load(self, file_path: str):
        logger.info(f"서빙용 모델을 로드합니다: {file_path}")
        try:
            model_uri = await get_model_uri(self._settings)
            self.model = lgb.Booster(model_file=model_uri)
            logger.info("서빙용 모델 로드가 완료되었습니다.")
            return True
        except Exception as e:
            logger.error(f"서빙용 모델 로드 중 오류가 발생했습니다: {str(e)}", exc_info=True)
            raise

if __name__ == '__main__':
    
    model = LightGBMRegressionModelServing()
    
    