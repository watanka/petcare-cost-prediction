import hydra
import mlflow
from omegaconf import DictConfig
from datetime import datetime
import os
import pandas as pd
from glob import glob

from src.configurations import Configurations
from src.middleware.db_client import DBClient
from src.middleware.logger import configure_logger
from src.jobs.retrieve import Retriever
from src.jobs.train import Trainer
from src.jobs.predict import Predictor
from src.jobs.register import DataRegister
from src.models.models import MODELS, find_latest_file
from src.models.preprocess import DataPreprocessPipeline

logger = configure_logger(__name__)

DATE_FORMAT = "%Y-%m-%d"


# @hydra.main(config_path="./hydra", config_name=Configurations.target_config_name)
def run(cfg: DictConfig):
    logger.info("학습 파이프라인을 시작합니다.")
    logger.info(f"config: {cfg}")

    cwd = os.getcwd()
    run_name = "-".join(cwd.split("/")[-2:])
    
    logger.info(f"current working directory: {cwd}")
    logger.info(f"run name: {run_name}")

    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URL", "http://mlflow:5000"))
    mlflow.set_experiment(cfg.name)

    with mlflow.start_run(run_name=run_name):
        # 데이터 설정
        data_preprocess_pipeline = DataPreprocessPipeline()
        data_preprocess_pipeline.define_pipeline()

        db_client = DBClient(cfg.jobs.data.db)
        data_retriever = Retriever(db_client)

        sql = """
        select pet_breed_id, birth, gender, neuter_yn, weight_kg, claim_price, pi.created_at, pi.updated_at 
        from pet as p left join pet_insurance_claim as pi on pi.pet_id=p.id 
        where type_of_claims="치료비" and status="접수"
        and pi.created_at between %s and %s
        ;
        """

        raw_df = data_retriever.retrieve_dataset(
            sql,
            date_from=cfg.jobs.data.details.date_from,
            date_to=cfg.jobs.data.details.date_to,
        )

        logger.info(
            f"""
            raw_data
            {raw_df}
            """
        )

        # 데이터 전처리 파이프라인
        xy_train, xy_test = data_retriever.train_test_split(
            raw_df, cfg.jobs.data.details.test_split_ratio, data_preprocess_pipeline
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
            preprocess_pipeline_file_path = os.path.join('/mlartifacts', f"{model.name}_{now}")
            save_file_path = os.path.join('/mlartifacts', f"{model.name}_{now}")

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
            mlflow.log_metric(
                "mean_absolute_percentage_error",
                evaluation.mean_absolute_percentage_error,
            )
            mlflow.log_metric(
                "root_mean_squared_error", evaluation.root_mean_squared_error
            )
            evaluation.eval_df.to_csv(os.path.join(cwd, "eval_df.csv"))
            mlflow.log_artifact(os.path.join(cwd, "eval_df.csv"), "eval_df")
            mlflow.log_artifact(artifact.preprocessed_file_path, "preprocess")
            mlflow.log_artifact(artifact.model_file_path, "model")

def predict(cfg: DictConfig, predict_df: pd.DataFrame):
    # TODO: 학습데이터만 들어왔을 때는 어떤 걸 평가하면 될까?
    cwd = os.getcwd()
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    db_client = DBClient(cfg.jobs.data.db)
    data_retriever = Retriever(db_client)

    sql = """
    select pet_breed_id, birth, gender, neuter_yn, weight_kg, claim_price, pi.created_at, pi.updated_at 
    from pet as p left join pet_insurance_claim as pi on pi.pet_id=p.id 
    where type_of_claims="치료비" and status="접수"
    and pi.created_at between %s and %s
    ;
    """

    raw_df = data_retriever.retrieve_dataset(
        sql,
        date_from=cfg.jobs.data.details.date_from,
        date_to=cfg.jobs.data.details.date_to,
    )

    logger.info(
        f"""
        raw_data
        {raw_df}
        """
    )
    
    predictor = Predictor()
    
    data_preprocess_pipeline = DataPreprocessPipeline()
    data_preprocess_pipeline.define_pipeline()
    
    # select latest
    # preprocess_pipeline_file_path = os.path.join(cwd, f"{model.name}_{now}")
    preprocess_pipeline_file_path = find_latest_file('/mlartifacts/', 'pkl')# '/mlartifacts/523829024154061849/9df127f976bb4c68b4b11c69db6c5baa/artifacts/preprocess/light_gbm_regression_20240516_143950.pkl'
    logger.info(f'preprocess pipeline: {preprocess_pipeline_file_path}')
    data_preprocess_pipeline.load_pipeline(preprocess_pipeline_file_path)
    
    
    
    _model = MODELS.get_model(name=cfg.jobs.model.name)
    model = _model.model(
        eval_metrics=cfg.jobs.model.eval_metrics,
    )
    
    
    txt_path = find_latest_file('/mlartifacts/', 'txt')
    logger.info(f"txt_path: {txt_path}")
    model.load_txt(txt_path)

    # if "params" in cfg.jobs.model.keys():
    #     model.reset_model(params=cfg.jobs.model.params)

    predictions = predictor.predict(
        model=model,
        data_preprocess_pipeline=data_preprocess_pipeline,
        previous_df = raw_df,
        data_to_be_predicted_df=predict_df,
    )

    logger.info(f"predictions: {predictions}")
    # 만약 결과를 등록하려면
    if cfg.jobs.predict.register:
        data_register = DataRegister()
        prediction_file_path = os.path.join('/data_storage', f"{model.name}_{now}")
        prediction_file_path = data_register.register(
            predictions=predictions, prediction_file_path=prediction_file_path
        )
        
    return predictions.tail(1)['prediction']


        
if __name__ == "__main__":
    run()
