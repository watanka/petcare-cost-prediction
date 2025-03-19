import hydra
import mlflow
from omegaconf import DictConfig
from datetime import datetime
import os
from glob import glob

from src.configurations import Configurations
from src.middleware.db_client import DBClient
from src.middleware.logger import configure_logger
from src.jobs.retrieve import Retriever
from src.jobs.train import Trainer
from src.models.models import MODELS


from src.models.preprocess import DataPreprocessPipeline

logger = configure_logger(__name__)

DATE_FORMAT = "%Y-%m-%d"
MLFLOW_ARTIFACT_PATH = os.getenv("MLFLOW_ARTIFACT_PATH", '/mlartifacts') # object storage


def print_auto_logged_info(run):
    tags = {k: v for k, v in run.data.tags.items() if not k.startswith("mlflow.")}
    artifacts = [
        f.path for f in mlflow.MlflowClient().list_artifacts(run.info.run_id, "model")
    ]
    feature_importances = [
        f.path
        for f in mlflow.MlflowClient().list_artifacts(run.info.run_id)
        if f.path != "model"
    ]
    print(f"run_id: {run.info.run_id}")
    print(f"artifacts: {artifacts}")
    print(f"feature_importances: {feature_importances}")
    print(f"params: {run.data.params}")
    print(f"metrics: {run.data.metrics}")
    print(f"tags: {tags}")



def train_model(cfg):

    data = cfg['data']['dataframe']

    data_retriever = Retriever()
    logger.info("학습 파이프라인을 시작합니다.")
    logger.info(f"config: {cfg}")
    
    cwd = os.getcwd()
    run_name = "-".join(cwd.split("/")[-2:])
    
    logger.info(f"current working directory: {cwd}")
    logger.info(f"run name: {run_name}")

    cfg.jobs.data.details.date_to =  datetime.now().strftime("%Y-%m-%d")
    cfg.jobs.train.run = True

    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URL", "http://localhost:5000"))
    logger.info(f"mlflow server url: {os.getenv('MLFLOW_TRACKING_URL', 'http://localhost:5000')}")
    mlflow.set_experiment(cfg.name)
    
    # lightgbm specified
    mlflow.lightgbm.autolog(registered_model_name="pet_insurance_claim_prediction")


    with mlflow.start_run(run_name=run_name) as run:
        # 데이터 설정
        data_preprocess_pipeline = DataPreprocessPipeline()
        data_preprocess_pipeline.define_pipeline()


        logger.info(
            f"""
            raw_data
            {data}
            """
        )

        # 데이터 전처리 파이프라인
        xy_train, xy_test = data_retriever.train_test_split(
            data, cfg.jobs.data.details.test_split_ratio, data_preprocess_pipeline
        )

        mlflow.log_param("target_date_date_from", cfg.jobs.data.details.date_from)
        mlflow.log_param("target_date_date_to", cfg.jobs.data.details.date_to)

        _model = MODELS.get_model(name=cfg.jobs.model.name)

        model = _model.model(
            eval_metrics=cfg.jobs.model.eval_metrics,
        )

        if "params" in cfg.jobs.model.keys():
            model.reset_model(params=cfg.jobs.model.params)
        
        
        if cfg.jobs.train.run:
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            preprocess_pipeline_file_path = os.path.join(MLFLOW_ARTIFACT_PATH, f"{model.model_name}_{now}") # model.model_name
            os.makedirs(preprocess_pipeline_file_path, exist_ok=True)
            save_file_path = os.path.join(MLFLOW_ARTIFACT_PATH, f"{model.model_name}_{now}")

            trainer = Trainer()

            evaluation, artifact = trainer.train_and_evaluate(
                model=model,
                x_train=xy_train.x,
                y_train=xy_train.y,
                x_test=xy_test.x,
                y_test=xy_test.y,
                data_preprocess_pipeline=data_preprocess_pipeline,
                preprocess_pipeline_file_path=preprocess_pipeline_file_path,
                save_file_path=save_file_path,
            )

            mlflow.log_metric("mean_absolute_error", evaluation.mean_absolute_error)
            mlflow.log_metric("mean_absolute_percentage_error", evaluation.mean_absolute_percentage_error)
            mlflow.log_metric("root_mean_squared_error", evaluation.root_mean_squared_error)
            
            evaluation.eval_df.to_csv(os.path.join(MLFLOW_ARTIFACT_PATH, f"{model.model_name}_{now}", "eval_df.csv"))
            mlflow.log_artifact(os.path.join(MLFLOW_ARTIFACT_PATH, f"{model.model_name}_{now}", "eval_df.csv"), "eval_df")
            mlflow.log_artifact(artifact.preprocessed_file_path, "preprocess")
            mlflow.log_artifact(artifact.model_file_path, "model")
        
        print_auto_logged_info(mlflow.get_run(run_id=run.info.run_id))
        
if __name__ == "__main__":
    main()
