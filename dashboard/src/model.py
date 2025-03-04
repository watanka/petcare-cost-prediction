

import pandas as pd
from logger import configure_logger
from schema import Breed, Gender, Neutralized
from typing import List, Optional
from abc import ABC

logger = configure_logger(__name__)


class Container(object):
    def __init__(self, insurance_claim_df: pd.DataFrame, prediction_df: pd.DataFrame):
        self.insurance_claim_df: pd.DataFrame =  insurance_claim_df
        self.prediction_df: pd.DataFrame = prediction_df




class BaseRepository(ABC):
    def select(
        self, container: Container   
    ):
        raise NotImplementedError

class BreedRepository(BaseRepository):
    def select(
        self,
        container: Container
    ) -> List[Breed]:
        breeds = container.insurance_claim_df.breed.unique()
        return [Breed(breed_name=breed) for breed in breeds]
    
class AgeRepository(BaseRepository):
    def select(
        self,
        container: Container
    ):
        pass
        
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
        neutralized = container.insurance_claim_df.neuter_yn.unique()
        return [Neutralized(n) for n in neutralized]



class ClaimPriceRepository(BaseRepository):
    def select(
        self,
        container: Container,
        variable_filter: List[str] = None,
    ):
        df = container.insurance_claim_df

        for variable in variable_filter:
            if variable != 'ALL':
                df = df[df[variable] == variable]
        return df
    
class ClaimPricePredictionRepository(BaseRepository):
    def select(
        self,
        container: Container,
        variable_filter: List[str] = None,
    ):
        df = container.prediction_df
        for variable in variable_filter:
            if variable != 'ALL':
                df = df[df[variable] == variable]
        return df