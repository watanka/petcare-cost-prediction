import pandas as pd
from typing import Optional, Tuple
from sklearn.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
)
from dataclasses import dataclass

from src.models.base_model import BasePetCareCostPredictionModel
from src.models.preprocess import DataPreprocessPipeline
from src.middleware.logger import configure_logger

logger = configure_logger(__name__)


@dataclass
class Evaluation:
    eval_df: pd.DataFrame
    mean_absolute_error: float
    mean_absolute_percentage_error: float
    root_mean_squared_error: float


class Artifact:
    preprocessed_file_path: Optional[str]
    model_file_path: Optional[str]


class Trainer:
    def __init__(self):
        pass

    def train(self, model, x_train, y_train, x_test, y_test):
        model.train (
            x_train=x_train, 
            y_train=y_train, 
            x_test=x_test, 
            y_test=y_test
            ) # eval_set = [(x_test, y_test)],

    def __organize_eval_df(self, df: pd.DataFrame):
        logger.info(
            '데이터 확인을 위해 추가적인 후처리 필요X'   
        )
        return df

    def __evaluate(self, df: pd.DataFrame):
        
        expensive_prediction_df = df[df["diff"] >= 100000]
        logger.info(
            f""" [실제값보다 10만원 이상 '높게' 예측한 데이터 # {len(expensive_prediction_df)}]
            {expensive_prediction_df}
            """
        )
        cheaper_prediction_df = df[df["diff"] <= -100000]
        logger.info(
            f""" [실제값보다 10만원 이상 '낮게' 예측한 데이터 # {len(cheaper_prediction_df)}]
            {cheaper_prediction_df}
            """
        )
        

    def evaluate(self, model, x, y):
        predictions = model.predict(x)
        eval_df = self.__organize_eval_df(df=x)
        eval_df = pd.concat(
            [pd.DataFrame(eval_df).reset_index(drop = True), pd.DataFrame({"y_true": y.claim_price.to_list(), "y_pred": predictions})],
            axis=1,
        )
        
        

        eval_df["diff"] = eval_df["y_true"] - eval_df["y_pred"]
        eval_df["error_rate"] = eval_df["diff"] / eval_df["y_true"]
        self.__evaluate(df=eval_df)

        rmse = mean_squared_error(
            y_true=eval_df.y_true, y_pred=eval_df.y_pred, squared=False
        )
        mae = mean_absolute_error(
            y_true=eval_df.y_true,
            y_pred=eval_df.y_pred,
        )

        mape = mean_absolute_percentage_error(
            y_true=eval_df.y_true,
            y_pred=eval_df.y_pred,
        )

        evaluation = Evaluation(
            eval_df=eval_df,
            mean_absolute_error=mae,
            mean_absolute_percentage_error=mape,
            root_mean_squared_error=rmse,
        )

        return evaluation

    def train_and_evaluate(
        self,
        model,
        x_train: pd.DataFrame,
        y_train: pd.DataFrame,
        x_test: pd.DataFrame,
        y_test: pd.DataFrame,
        data_preprocess_pipeline: Optional[DataPreprocessPipeline] = None,
        preprocess_pipeline_file_path: Optional[str] = None,
        save_file_path: Optional[str] = None,
    ) -> Tuple[Evaluation, Artifact]:
        self.train(
            model=model,
            x_train=x_train,
            y_train=y_train,
            x_test=x_test,
            y_test=y_test,
        )
        

        evaluation = self.evaluate(model=model, x=x_test, y=y_test)

        artifact = Artifact()
        if (
            data_preprocess_pipeline is not None
            and preprocess_pipeline_file_path is not None
        ):
            artifact.preprocessed_file_path = data_preprocess_pipeline.dump_pipeline(
                file_path=preprocess_pipeline_file_path
            )

        if save_file_path is not None:
            model.save(save_file_path) # bst ext
            artifact.model_file_path = save_file_path

        return evaluation, artifact

    def export_onnx(self):
        pass