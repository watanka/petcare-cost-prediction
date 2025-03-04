from datetime import date
from typing import List, Optional

import numpy as np
import pandas as pd
from logger import configure_logger

from schema import Breed, Gender
from model import (Container, 
                   BaseRepository,
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

class ServiceFactory:
    @staticmethod
    def get_service(service_name: str) -> BaseService:
        if service_name == 'gender':
            repository = GenderRepository()
        elif service_name == 'neutralized':
            repository = NeutralizedRepository()
        elif service_name == 'breed':
            repository = BreedRepository()
        elif service_name == 'age':
            repository = AgeRepository()
        return CategoryService(repository)


class CategoryService(BaseService):
    def __init__(self, repository: BaseRepository):
        super().__init__()
        self.repository = repository

    def list_labels(self, container: Container) -> List[str]:
        variables = self.repository.select(container=container)
        variable_names = [v.value for v in variables]
        return variable_names


class ClaimPriceService(BaseService):
    def __init__(self):
        super().__init__()
        self.claim_prices_repository = ClaimPriceRepository()

    def retrieve_claim_prices(
        self,
        container: Container,
        variable_filter: List[str] = None,
    ) -> pd.DataFrame:
        df = self.claim_prices_repository.select(
            container=container,
            variable_filter=variable_filter,
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
        variable_filter: List[str] = None,
    ) -> pd.DataFrame:
        predictions_df = self.claim_price_predictions_repository.select(
            container=container,
            variable_filter = variable_filter,
        )
        predictions_df.drop("claim_price", axis=1, inplace=True)
        logger.info(
            f"""
prediction df
    df shape: {predictions_df.shape}
    df columns: {predictions_df.columns}
                """
        ) 
        claim_price_evaluation_df = pd.merge(
            claim_price_df,
            predictions_df,
            on=["claim_id"],
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
                "neutralized",
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