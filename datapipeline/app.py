from fastapi import FastAPI
from hydra import initialize, compose
from datetime import datetime, date
import pandas as pd

import json
import uvicorn
from pydantic import BaseModel


import execute
from src.middleware.logger import configure_logger

logger = configure_logger(__name__)


class PetInfo(BaseModel):
    pet_breed_id: int
    birth: date
    gender: str
    neuter_yn: str
    weight_kg: float
    created_at: datetime
    
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
    
    df = pd.read_csv('/data_storage/petcare_statistics.csv', index_col = 0)
    res = df.to_json(orient = 'records')
    parsed = json.loads(res)
    
    return parsed
    
    


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)