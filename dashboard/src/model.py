import pandas as pd
from logger import configure_logger
from schema import Breed, Gender, Neutralized, District
from typing import List, Optional
from abc import ABC
import os
from configurations import Configurations
logger = configure_logger(__name__)


class Container(object):
    def __init__(self):
        self.config = Configurations()
        self.insurance_claim_df: pd.DataFrame =  None
        self.prediction_df: pd.DataFrame = None

    def set_insurance_claim_df(self, df: pd.DataFrame):
        self.insurance_claim_df = df

    def set_prediction_df(self, df: pd.DataFrame):
        self.prediction_df = df


class BaseRepository(ABC):
    def select(
        self, container: Container   
    ):
        raise NotImplementedError

## 옵션 항목 저장소
class DistrictRepository(BaseRepository):
    def select(
        self,
        container: Container
    ) -> List[District]:
        districts = container.insurance_claim_df.district.unique()
        return [District(district) for district in districts]

class BreedRepository(BaseRepository):
    def select(
        self,
        container: Container
    ) -> List[Breed]:
        breeds = container.insurance_claim_df.breed.unique()
        return [Breed(breed) for breed in breeds]
    
class AgeRepository(BaseRepository):
    def select(
        self,
        container: Container
    ):
        age_range = (container.insurance_claim_df.age.min(), container.insurance_claim_df.age.max())
        
        return age_range
        
class GenderRepository(BaseRepository):
    def select(
        self,
        container: Container
    )-> List[Gender]:
        genders = container.insurance_claim_df.gender.unique()
        return [Gender(gender) for gender in genders]

class NeutralizedRepository(BaseRepository):
    def select(
        self,
        container: Container
    )-> List[Neutralized]:
        neutralized = container.insurance_claim_df.neutralized.unique()
        return [Neutralized(n) for n in neutralized]

class DateRepository(BaseRepository):
    def select(self,container: Container)-> List[str]:
        _options = os.listdir(container.config.insurance_claim_records_dir)
        options = ['ALL']
        options.extend(_options)
        return options
    
class ModelRepository(BaseRepository):
    def select(self, container: Container) -> List[str]:
        options = os.listdir(container.config.insurance_claim_prediction_dir)
        return options

