from datetime import datetime
import os
import mlflow
from functools import wraps

from src.preprocess import split_train_test
from src.model_trainer import Trainer
from src.models.models import MODELS
from src.preprocess import DataPreprocessPipeline
from src.logger import setup_logger

logger = setup_logger(__name__)

DATE_FORMAT = "%Y-%m-%d"
MLFLOW_ARTIFACT_PATH = os.getenv("MLFLOW_ARTIFACT_PATH", '/mlartifacts')

def with_mlflow(enabled=True):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cfg = kwargs.get('cfg', args[0] if args else None)
            if not cfg:
                return func(*args, **kwargs)

            if not enabled:
                evaluation, artifact = func(*args, **kwargs)
                return {
                    "run_id": cfg['run_name'],
                    "evaluation": evaluation,
                    "artifact": artifact
                }
            
            cwd = os.getcwd()
            run_name = "-".join(cwd.split("/")[-2:])
            
            mlflow.set_tracking_uri(cfg['mlflow']['tracking_uri'])
            mlflow.set_experiment(cfg['name'])
            mlflow.lightgbm.autolog(registered_model_name="pet_insurance_claim_prediction")

            with mlflow.start_run(run_name=run_name) as run:
                evaluation, artifact = func(*args, **kwargs)
                
                # MLflow 메트릭 로깅
                mlflow.log_metric("mean_absolute_error", evaluation.mean_absolute_error)
                mlflow.log_metric("mean_absolute_percentage_error", evaluation.mean_absolute_percentage_error)
                mlflow.log_metric("root_mean_squared_error", evaluation.root_mean_squared_error)
                
                # MLflow 아티팩트 로깅
                save_dir = os.path.join(MLFLOW_ARTIFACT_PATH, f"{artifact.model.model_name}_{run.info.run_id}")
                evaluation.eval_df.to_csv(os.path.join(save_dir, "eval_df.csv"))
                mlflow.log_artifact(os.path.join(save_dir, "eval_df.csv"), "eval_df")
                mlflow.log_artifact(artifact.preprocessed_file_path, "preprocess")
                mlflow.log_artifact(artifact.model_file_path, "model")
                
                return {
                    "run_id": cfg['run_name'],
                    "evaluation": evaluation,
                    "artifact": artifact
                }
        return wrapper
    return decorator

@with_mlflow(enabled=False)  # MLflow 사용 여부를 여기서 설정
def train_model(cfg):
    data = cfg['data']['dataframe']

    logger.info("학습 파이프라인을 시작합니다.")
    logger.info(f"config: {cfg}")
    logger.info(f"데이터프레임 컬럼: {data.columns.tolist()}")
    
    # 데이터 설정
    data_preprocess_pipeline = DataPreprocessPipeline(config={
        "columns": {
            "age": {"type": "numeric", "handling": "standard_scale"},
            "gender": {"type": "categorical", "handling": "one_hot"},
            "breed": {"type": "categorical", "handling": "one_hot"},
            "neutralized": {"type": "categorical", "handling": "one_hot"},
            "weight": {"type": "numeric", "handling": "standard_scale"},
        }
    })
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
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_dir = os.path.join("results", f"{model.model_name}_{now}")
    os.makedirs(save_dir, exist_ok=True)

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

    # 결과 저장
    evaluation.eval_df.to_csv(os.path.join(save_dir, "eval_df.csv"))
    
    logger.info(f"학습 완료. 결과가 {save_dir}에 저장되었습니다.")
    logger.info(f"평가 지표:")
    logger.info(f"- MAE: {evaluation.mean_absolute_error:.2f}")
    logger.info(f"- MAPE: {evaluation.mean_absolute_percentage_error:.2f}%")
    logger.info(f"- RMSE: {evaluation.root_mean_squared_error:.2f}")

    return evaluation, artifact

