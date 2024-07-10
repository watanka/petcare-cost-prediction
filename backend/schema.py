from pydantic import BaseModel
from dataclasses import dataclass
from datetime import datetime, date
import pandas as pd



@dataclass
class XY:
    x: pd.DataFrame
    y: pd.DataFrame


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
