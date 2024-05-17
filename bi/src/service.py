from datetime import date
from typing import List, Optional

import numpy as np
import pandas as pd
from logger import configure_logger

from schema import Breed, Gender
from model import (Container, 
                   BreedRepository, 
                   AgeRepository,
                   GenderRepository,
                   NeutralizedRepository,
                   ClaimPriceRepository, 
                   ClaimPricePredictionRepository)


logger = configure_logger(__name__)



class BaseService(object):
    def __init__(self):
        pass


class CategoryService(BaseService):
    def list_labels(self):
        raise NotImplementedError
    
class GenderService(BaseService):
    def __init__(self):
        super().__init__()
        self.gender_repository = GenderRepository()
    
    def list_labels(self, container: Container) -> List[str]:
        genders = self.gender_repository.select(container=container)
        gender_name = [g.name for g in genders]
        return gender_name

class NeutralizedService(BaseService):
    def __init__(self):
        super().__init__()
        self.neutralized_repository = NeutralizedRepository()
    
    def list_labels(self, container: Container) -> List[str]:
        neutralized = self.neutralized_repository.select(container=container)
        neutralized_name = [n.name for n in neutralized]
        return neutralized_name



class AgeService(BaseService):
    def __init__(self):
        super().__init__()
        self.age_repository = AgeRepository()

    def list_breeds(
        self,
        container: Container,
    ) -> List[str]:
        breeds = self.breed_repository.select(container=container)
        breed_names = [b.name for b in breeds]
        return breed_names

class BreedService(BaseService):
    def __init__(self):
        super().__init__()
        self.breed_repository = BreedRepository()

    def list_breeds(
        self,
        container: Container,
    ) -> List[str]:
        breeds = self.breed_repository.select(container=container)
        breed_names = [b.name for b in breeds]
        return breed_names

class ClaimPriceService(BaseService):
    def __init__(self):
        super().__init__()
        self.claim_prices_repository = ClaimPriceRepository()

    def retrieve_claim_prices(
        self,
        container: Container,
        breed: Optional[Breed] = None,
        age: Optional[int] = None,
        gender: Optional[Gender] = None,
        neutralized: Optional[bool] = None,
    ) -> pd.DataFrame:
        df = self.claim_prices_repository.select(
            container=container,
            breed=breed,
            age=age,
            gender=gender,
            neutralized=neutralized,
        )
        return df

class ClaimPricePredictionService(BaseService):
    def __init__(self):
        super().__init__()
        self.claim_price_predictions_repository = ClaimPricePredictionRepository()

    def aggregate_price_evaluation(
        self,
        container: Container,
        claim_price_df: pd.DataFrame,
        breed: Optional[Breed] = None,
        age: Optional[int] = None,
        gender: Optional[Gender] = None,
        neutralized: Optional[bool] = None,
    ) -> pd.DataFrame:
        predictions_df = self.claim_price_predictions_repository.select(
            container=container,
            breed = breed,
            age = age,
            gender = gender,
            neutralized = neutralized,
        )
        predictions_df.drop("claim_price", axis=1, inplace=True)
        logger.info(
            f"""
weekly prediction df
    df shape: {predictions_df.shape}
    df columns: {predictions_df.columns}
                """
        ) 
        claim_price_evaluation_df = pd.merge(
            claim_price_df,
            predictions_df,
            on=["pet_breed_id", "gender", "neuter_yn", "weight_kg", "age"],
            how="inner",
        )
        claim_price_evaluation_df["diff"] = (
            claim_price_evaluation_df["claim_price"].astype("float") - claim_price_evaluation_df["prediction"]
        )
        claim_price_evaluation_df["error_rate"] = claim_price_evaluation_df["diff"] / claim_price_evaluation_df["claim_price"].astype("float")
        claim_price_evaluation_df = claim_price_evaluation_df[
            [
                "pet_breed_id",
                "gender",
                "neuter_yn",
                "weight_kg",
                "age",
                "claim_price",
                "prediction",
                "diff",
                "error_rate",
            ]
        ]
        logger.info(
            f"""
weekly sales evaluation df
    df shape: {claim_price_evaluation_df.shape}
    df columns: {claim_price_evaluation_df.columns}
"""
        )
        return claim_price_evaluation_df