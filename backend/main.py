from fastapi import FastAPI
from contextlib import asynccontextmanager

import os

from hydra import initialize, compose
import uvicorn
import requests
# from elasticapm.contrib.starlette import  ElasticAPM
# from src.middleware.apm import apm

from utils import preprocess_request_input, convert_prediction_input, postprocess_output, find_latest_file
from schema import PetInfo, PetPredictResult
from db_client import DBClient
# from src.middleware.exception import ExceptionHandlerMiddleware
from summarize import Statistics

from retrieve import Retriever
from preprocess import DataPreprocessPipeline

from logger import configure_logger



logger = configure_logger(__name__)


MLSERVER_URL = os.getenv('MLSERVER_URL', "http://localhost:8080")
MLSERVER_ENDPOINT = os.getenv('MLSERVER_ENDPOINT',"/v2/models/petcare-prediction-serving/infer")
MLFLOW_ARTIFACT_PATH= os.getenv('MLFLOW_ARTIFACT_PATH', "")


@asynccontextmanager
async def lifespan(app: FastAPI):
    with initialize(config_path="./hydra"):
        app.cfg = compose(config_name="base.yaml")
        
    db_client = DBClient(app.cfg.jobs.data.db)
    data_retriever = Retriever(db_client)
    app.data_retriever = data_retriever
    
    # select pet_breed_id, birth, gender, neuter_yn, weight_kg, claim_price, pi.created_at, pi.updated_at 
    # from pet as p left join pet_insurance_claim as pi on pi.pet_id=p.id 
    # where type_of_claims="치료비" and status="접수"
    # and pi.created_at between %s and %s
    # ;
    
    app.sql_query = """
    SELECT pet_breed_id, birth, age, gender, neuter_yn, weight_kg, claim_price, disease_name
    FROM pet_insurance_claim_ml_fake_data;
    """

    app.raw_df = app.data_retriever.retrieve_dataset(app.sql_query)
                                    #(app.cfg.jobs.data.details.date_from, app.cfg.jobs.data.details.date_to))
    app.breeds_categories_used_in_train = app.raw_df['pet_breed_id'].unique()
    
    logger.info(
        f"""
        raw_data
        {app.raw_df}
        """
    )
    
    
    app.data_preprocess_pipeline = DataPreprocessPipeline()
    app.data_preprocess_pipeline.define_pipeline()
    
    # select latest
    # preprocess_pipeline_file_path = os.path.join(cwd, f"{model.name}_{now}")
    preprocess_pipeline_file_path = 'light_gbm_regression_serving_20240618_041413.pkl' # find_latest_file(MLFLOW_ARTIFACT_PATH, 'pkl')# '/mlartifacts/523829024154061849/9df127f976bb4c68b4b11c69db6c5baa/artifacts/preprocess/light_gbm_regression_20240516_143950.pkl'
    logger.info(f'preprocess pipeline: {preprocess_pipeline_file_path}')
    app.data_preprocess_pipeline.load_pipeline(preprocess_pipeline_file_path)
    
    yield
    
        
    

app = FastAPI(lifespan=lifespan)
# app.add_middleware(ExceptionHandlerMiddleware)
# app.add_middleware(ElasticAPM, client=apm)

    
    
@app.post('/predict')
def predict(requestInfo: PetInfo) -> PetPredictResult:
    preprocessed_data = preprocess_request_input(app.breeds_categories_used_in_train, 
                                                 app.data_preprocess_pipeline,
                                                 requestInfo)
    data = convert_prediction_input(preprocessed_data)
    response = requests.post(MLSERVER_URL + MLSERVER_ENDPOINT, json = data)
    output = postprocess_output(requestInfo, response)
    
    return output
    
@app.get('/statistics') # cache 설정
def statistics(breed_id: int):
    
    sql_query = """
    SELECT pet_breed_id, birth, age, gender, neuter_yn, weight_kg, claim_price, disease_name
    FROM pet_insurance_claim_ml_fake_data
    WHERE pet_breed_id = %s;
    """
    
    df = app.data_retriever.retrieve_dataset(sql_query, (breed_id))
    df = app.data_preprocess_pipeline.preprocess(df, app.breeds_categories_used_in_train)
    stat = Statistics(df)
    res = stat.aggregate_stat(breed_id)
    
    return res
    
    


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)