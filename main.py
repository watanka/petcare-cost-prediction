import hydra
from omegaconf import DictConfig
from src.configurations import Configurations
from src.jobs.retrieve import Retriever
from src.models.preprocess import DataPreprocessPipeline, AgeCalculator

@hydra.main(
    config_path="./hydra",
    config_name=Configurations.target_config_name
)
def main(cfg: DictConfig):
    
    print(cfg.jobs.data.db)
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
    
    raw_df = data_retriever.retrieve_dataset(sql, date_from = cfg.jobs.data.details.date_from, date_to = cfg.jobs.data.details.date_to)
    print(raw_df)
    
    # 데이터 전처리 파이프라인
    xy_train, xy_test = data_retriever.train_test_split(
        raw_df,
        cfg.jobs.data.details.test_split_ratio,
        data_preprocess_pipeline
    )

    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import FunctionTransformer, MinMaxScaler, OneHotEncoder
    import pandas as pd
    import datetime
    import numpy as np
    
    # pipeline = ColumnTransformer(
    #         transformers = [
    #             # ('simple_imputer', SimpleImputer(missing_values=np.nan, strategy = 'constant', fill_value = None), ['pet_breed_id', 'birth', 'gender', 'neuter_yn', 'weight_kg']),
    #             ('one_hot_encoder', OneHotEncoder(), ['gender', 'neuter_yn']),
    #             ('age_calculator', AgeCalculator(), ['birth', 'created_at']),
    #             ('min_max_scaler', MinMaxScaler(), ['weight_kg']),
    #         ]
    #     )

    # pipeline.fit(xy_train.x)
    # _x = pipeline.transform(xy_train.x)
    print(xy_train)
        
    # trainer = Trainer()


if __name__ == '__main__':
    main()