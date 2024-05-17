from datetime import datetime
from pandera import Column, DataFrameSchema, Check, Index
from pydantic import BaseModel, Extra
from typing import List
from enum import Enum

class Gender(Enum):
    남자 = "남자"
    여자 = "여자" 
    
class Breed(BaseModel):
    name: int # TODO: 품종 이름 매칭
    class Config:
        extra = Extra.forbid

class Neutralized(Enum):
    y = "y"
    n = "n"
    


# class Pet(BaseModel):
#     gender: Enum
#     breed: Enum
#     age: int
#     neutralized: bool
#     weight: float
    

# class InsuranceClaim(BaseModel):
#     date: datetime
#     case: Enum
#     user: User
#     pet: Pet
    
#     claim_price: float
    
#     class Config:
#         extra = Extra.forbid


# class User(BaseModel):
#     gender: Enum    
#     age: int
#     address: str
#     pets: List[Pet]
#     claims: List[InsuranceClaim]


