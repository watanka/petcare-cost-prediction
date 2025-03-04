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
    def get_service(service_name: str, variable_type: str) -> BaseService:
        '''
        variable_type: [category, numeric]
        '''
        if variable_type == 'category':
            if service_name == 'gender':
                repository = GenderRepository()
            elif service_name == 'neutralized':
                repository = NeutralizedRepository()
            elif service_name == 'breed':
                repository = BreedRepository()
            return CategoryService(repository)
        
        elif variable_type == 'numeric':
            if service_name == 'age':
                repository = AgeRepository()
            return NumericService(repository)
        else:
            raise ValueError(f"Invalid service name: {service_name}")
        


class CategoryService(BaseService):
    def __init__(self, repository: BaseRepository):
        super().__init__()
        self.repository = repository

    def list_labels(self, container: Container) -> List[str]:
        variables = self.repository.select(container=container)
        logger.info(f"variables: {variables}")
        variable_names = [v.value for v in variables]
        return variable_names

class NumericService(BaseService):
    def __init__(self, repository: BaseRepository):
        super().__init__()
        self.repository = repository

    def list_labels(self, container: Container) -> List[str]:
        value_range = self.repository.select(container=container)
        logger.info(f"value_range: {value_range}")
        return value_range
        
        
    

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

    def calculate_district_statistics(
        self,
        container: Container,
        claim_price_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        구별 평균 청구금액, 예측금액, 오차율 등을 계산
        """
        # 예측 데이터 가져오기
        predictions_df = self.claim_price_predictions_repository.select(container=container)
        
        # 청구 데이터와 예측 데이터 병합
        merged_df = pd.merge(
            claim_price_df,
            predictions_df,
            on=["claim_id"],
            how="left"
        )
        
        # 구별 통계 계산
        district_stats = merged_df.groupby('district').agg({
            'price': ['mean', 'count'],
            'predicted_price': 'mean',
        }).round(0)
        
        # 컬럼명 정리
        district_stats.columns = [
            'avg_claim_price',
            'claim_count',
            'avg_predicted_price'
        ]
        district_stats = district_stats.reset_index()
        
        # 오차 계산
        district_stats['price_diff'] = district_stats['avg_predicted_price'] - district_stats['avg_claim_price']
        district_stats['error_rate'] = (district_stats['price_diff'] / district_stats['avg_claim_price'] * 100).round(2)
        
        return district_stats

    def aggregate_price_evaluation(
        self,
        container: Container,
        claim_price_df: pd.DataFrame,
    ) -> pd.DataFrame:
        '''
        드랍다운에 의한 filtering은 claim_price_df에서 이루어짐
        '''
        predictions_df = self.claim_price_predictions_repository.select(container=container)
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
            how="left",
        )
        claim_price_evaluation_df["diff"] = (
            claim_price_evaluation_df["predicted_price"].astype("float") - claim_price_evaluation_df["price"]
        )
        claim_price_evaluation_df["error_rate"] = claim_price_evaluation_df["diff"] / claim_price_evaluation_df["price"].astype("float")
        claim_price_evaluation_df = claim_price_evaluation_df[
            [
                "breed",
                "gender",
                "neutralized",
                "weight",
                "age",
                "price",
                "predicted_price",
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