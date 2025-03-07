from pydantic import BaseModel, Field
from typing import Optional, List
from models.enums import District, Gender, Breed, Neutralized

class Pet(BaseModel):
    """반려동물 모델"""
    pet_id: str
    gender: Gender
    breed: Breed
    neutralized: Neutralized
    district: District
    age: int
    weight: float

class InsuranceClaim(BaseModel):
    """보험 청구 모델"""
    claim_id: str
    pet_id: str
    gender: Gender
    breed: Breed
    neutralized: Neutralized
    district: District
    age: int
    weight: float
    price: int
    issued_at: str

class PredictionResult(BaseModel):
    """예측 결과 모델"""
    claim_id: str
    predicted_price: int

class ModelMetrics(BaseModel):
    """모델 성능 지표 모델"""
    model_name: str
    avg_price: float
    avg_pred: float
    avg_diff: float
    avg_error: float
    mse: float
    rmse: float
    mae: float

class FilterOption(BaseModel):
    """필터 옵션 모델"""
    variable_name: str
    variable_type: str
    selected_value: any