import pandas as pd
from logger import configure_logger
from schema import Breed, Gender, Neutralized, District
from typing import List, Optional
from abc import ABC
import os

logger = configure_logger(__name__)


class Container(object):
    def __init__(self):
        self.insurance_claim_df: pd.DataFrame =  None
        self.prediction_df: pd.DataFrame = None

    def load_insurance_claim_df(self, file_path: str):
        self.insurance_claim_df = pd.read_csv(file_path)

    def load_prediction_df(self, file_path: str):
        self.prediction_df = pd.read_csv(file_path)

    def combine_records(self, df_list: list[pd.DataFrame]):
        df = pd.concat(df_list)
        self.prediction_df = df
        return df


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
