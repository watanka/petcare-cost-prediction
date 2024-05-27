from fastapi import FastAPI, HTTPException
from hydra import initialize, compose
from datetime import datetime, date
import pandas as pd

import json
import uvicorn
from pydantic import BaseModel


import execute
from src.jobs.summarize import Statistics
from src.middleware.logger import configure_logger


logger = configure_logger(__name__)




class PetInfo(BaseModel):
    pet_breed_id: int
    birth: date
    gender: str
    neuter_yn: str
    weight_kg: float
    created_at: datetime = datetime.now()#.strftime("%Y-%m-%d %H:%M:%S")
    
class PetPredictResult(BaseModel):
    pet_breed_id: int
    age: int
    gender: str
    neuter_yn: str
    weight_kg: float
    predicted_claim_price: float

app = FastAPI()


@app.post('/train')
def train():
    # 기존 설정 로드
    with initialize(config_path="./hydra"):
        cfg = compose(config_name="base.yaml")

    cfg.jobs.data.details.date_to =  datetime.now().strftime("%Y-%m-%d")
    
    execute.run(cfg)
    
@app.post('/predict')
def predict(requestInfo: PetInfo):
    with initialize(config_path="./hydra"):
        cfg = compose(config_name="base.yaml")

    cfg.jobs.data.details.date_to =  datetime.now().strftime("%Y-%m-%d")
    cfg.jobs.train.run = False
    cfg.jobs.predict.register = False
    
    
    predicted_claim_price = execute.predict(cfg, pd.DataFrame([requestInfo.dict()]))

    age = requestInfo.created_at.date() - requestInfo.birth
    
    return PetPredictResult(
        pet_breed_id=requestInfo.pet_breed_id,
        age=age.days // 30 // 12,
        gender=requestInfo.gender,
        neuter_yn=requestInfo.neuter_yn,
        weight_kg=requestInfo.weight_kg,
        predicted_claim_price=round(predicted_claim_price/1000)* 1000
    )
    
@app.get('/statistics')
def statistics(breed_id: int):
    
    df = pd.read_csv('/data_storage/fake_petinsurance_chart.csv', index_col = 0)
    stat = Statistics(df)
    try :
        res = stat.aggregate_stat(breed_id)
    except KeyError as e:
        raise HTTPException(status_code = 404, detail = "해당 견종은 아직 축적된 데이터가 없습니다.")
    
    return res
    
    


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)