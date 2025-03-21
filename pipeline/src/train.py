from datetime import datetime
import os
import mlflow
from functools import wraps
import json

from src.preprocess import split_train_test
from src.model_trainer import Trainer
from src.models.models import MODELS
from src.preprocess import DataPreprocessPipeline
from src.logger import setup_logger
from src.experiment import ExperimentTracker
logger = setup_logger(__name__)

DATE_FORMAT = "%Y-%m-%d"
ARTIFACT_PATH = os.getenv("ARTIFACT_PATH", './data_storage/train_results')

def train_model(cfg):
    model_name = cfg['model']['name']
    data = cfg['data']['dataframe']
    run_name = cfg['run_name']
    logger.info("학습 파이프라인을 시작합니다.")
    logger.info(f"config: {cfg}")
    logger.info(f"데이터프레임 컬럼: {data.columns.tolist()}")
    
    experiment_name = f"{model_name}_{run_name}"
    save_dir = os.path.join(ARTIFACT_PATH, experiment_name)
    tracker = ExperimentTracker(save_dir=save_dir)

    # 데이터 설정
    data_preprocess_pipeline = DataPreprocessPipeline(cfg['preprocessing'])
    data_preprocess_pipeline.define_pipeline()

    logger.info(f"raw_data\n{data}")

    # 데이터 분할 및 전처리
    xy_train, xy_test = split_train_test(
        raw_df=data,
        test_split_ratio=0.2,
        data_preprocess_pipeline=data_preprocess_pipeline
    )

    # 모델 초기화
    _model = MODELS.get_model(name=cfg['model']['name'])
    model = _model.model()
    
    if "params" in cfg['model'].keys():
        model.reset_model(params=cfg['model']['params'])
        
    model.set_eval_metrics(eval_metrics=cfg['model']['eval_metrics'])

    # 결과 저장 경로 설정
    
    # 학습 및 평가
    trainer = Trainer()
    evaluation, artifact = trainer.train_and_evaluate(
        model=model,
        x_train=xy_train.x,
        y_train=xy_train.y,
        x_test=xy_test.x,
        y_test=xy_test.y,
        data_preprocess_pipeline=data_preprocess_pipeline,
        preprocess_pipeline_file_path=save_dir,
        save_file_path=save_dir,
    )

    tracker.log_experiment({
        # 실험 정보
        "experiment_name": cfg['name'],
        "run_name": cfg['run_name'],
        
        # 데이터 설정
        "data_source": str(cfg['data']['source']),
        "date_from": cfg['data']['details']['date_from'],
        "date_to": cfg['data']['details']['date_to'],
        "test_split_ratio": cfg['data']['details']['test_split_ratio'],
        
        # 모델 설정
        "model_name": cfg['model']['name'],
        "eval_metrics": cfg['model']['eval_metrics'],
        "num_leaves": cfg['model']['params']['num_leaves'],
        "learning_rate": cfg['model']['params']['learning_rate'],
        "feature_fraction": cfg['model']['params']['feature_fraction'],
        "max_depth": cfg['model']['params']['max_depth'],
        "num_iterations": cfg['model']['params']['num_iterations'],
        "early_stopping_rounds": cfg['model']['params']['early_stopping_rounds'],
        
        # 전처리 설정
        "preprocessing_columns": str(list(cfg['preprocessing']['columns'].keys())),
        "drop_columns": str(cfg['preprocessing']['drop_columns'])
    })

    tracker.log_metric("mean_absolute_error", evaluation.mean_absolute_error)
    tracker.log_metric("mean_absolute_percentage_error", evaluation.mean_absolute_percentage_error)
    tracker.log_metric("root_mean_squared_error", evaluation.root_mean_squared_error)

    tracker.save_metric()

    # 결과 저장
    evaluation.eval_df.to_csv(os.path.join(save_dir, "eval_df.csv"))
    
    logger.info(f"학습 완료. 결과가 {save_dir}에 저장되었습니다.")
    logger.info(f"평가 지표:")
    logger.info(f"- MAE: {evaluation.mean_absolute_error:.2f}")
    logger.info(f"- MAPE: {evaluation.mean_absolute_percentage_error:.2f}%")
    logger.info(f"- RMSE: {evaluation.root_mean_squared_error:.2f}")

    return evaluation, artifact