import hydra
from omegaconf import DictConfig
from datetime import datetime
import os

from src.configurations import Configurations
from src.jobs.retrieve import Retriever
from src.jobs.train import Trainer
from src.jobs.predict import Predictor
from src.jobs.register import DataRegister
from src.models.models import MODELS
from src.models.preprocess import DataPreprocessPipeline, calculate_age

from shapash import SmartExplainer

@hydra.main(
    config_path="./hydra",
    config_name=Configurations.target_config_name
)
def main(cfg: DictConfig):
    
    cwd = os.getcwd()
    # experiment 설정
    # mlflow experiment 설정
    
    
    # 데이터 설정
    data_preprocess_pipeline = DataPreprocessPipeline()
    data_preprocess_pipeline.define_pipeline()
    
    data_retriever = Retriever(**cfg.jobs.data.db)
    
    sql = '''
    select pet_breed_id, birth, gender, neuter_yn, weight_kg, claim_price, pi.created_at, pi.updated_at 
    from pet as p left join pet_insurance_claim as pi on pi.pet_id=p.id 
    where type_of_claims="치료비" and status="접수"
    and pi.created_at between %s and %s
    ;
    '''
    
    raw_df = data_retriever.retrieve_dataset(sql, 
                                             date_from = cfg.jobs.data.details.date_from, 
                                             date_to = cfg.jobs.data.details.date_to)
    
    
    # 데이터 전처리 파이프라인
    xy_train, xy_test = data_retriever.train_test_split(
        raw_df,
        cfg.jobs.data.details.test_split_ratio,
        data_preprocess_pipeline
    )

    _model = MODELS.get_model(name = cfg.jobs.model.name)
    
    model = _model.model(
        eval_metrics = cfg.jobs.model.eval_metrics,
    )
    
    print(xy_train.x)
    print(xy_test.y)
    
    if 'params' in cfg.jobs.model.keys():
        model.reset_model(params = cfg.jobs.model.params)
    
    if cfg.jobs.train.run:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        preprocess_pipeline_file_path = os.path.join(cwd, f"{model.name}_{now}")
        save_file_path = os.path.join(cwd, f"{model.name}_{now}")
        
        trainer = Trainer()
        
        evaluation, artifact = trainer.train_and_evaluate(
            model=model,
            x_train=xy_train.x,
            y_train=xy_train.y,
            x_test=xy_test.x,
            y_test=xy_test.y,
            data_preprocess_pipeline=data_preprocess_pipeline,
            preprocess_pipeline_file_path=preprocess_pipeline_file_path,
            save_file_path=save_file_path
        )
        
        eval_df = evaluation.eval_df
        
        
        
        print(data_preprocess_pipeline.inverse_transform(evaluation.eval_df))
        print(artifact.preprocessed_file_path)
        print(artifact.model_file_path)

    
    if cfg.jobs.predict.run:
        # TODO: 학습데이터만 들어왔을 때는 어떤 걸 평가하면 될까?
        
        predictor = Predictor()

        predictions = predictor.predict(
                model=model,
                data_preprocess_pipeline=data_preprocess_pipeline,
                df=raw_df
            )
        
        # 만약 결과를 등록하려면
        if cfg.jobs.predict.register:
            data_register = DataRegister()
            prediction_file_path = os.path.join(cwd, f'{model.name}_{now}')
            prediction_file_path = data_register.register(
                predictions = predictions,
                prediction_file_path = prediction_file_path
            )
    


if __name__ == '__main__':
    main()