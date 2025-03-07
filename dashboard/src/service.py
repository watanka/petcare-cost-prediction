import pandas as pd
from logger import configure_logger
from typing import List, Tuple
from abc import ABC, abstractmethod
from model import Container
import os

logger = configure_logger(__name__)


class DataService(ABC):
    @abstractmethod
    def retrieve(self, container: Container, variable_filter: List[str]) -> pd.DataFrame:
        pass


class DataStatisticsService:
    def retrieve(
        self,
        container: Container,
        variable_filter: List[Tuple[str, str]] = None,
    ) -> pd.DataFrame:
        df = container.insurance_claim_df
        logger.info(f"df: {df.columns}")
        logger.info(f"variable_filter: {variable_filter}")
        try: 
            for variable_name, selected in variable_filter:
                logger.info(f"variable_name: {variable_name}, selected: {selected}")
                if selected == 'ALL':
                    continue
                if variable_name == 'age':
                    df = df[(df[variable_name] >= selected[0]) & (df[variable_name] <= selected[1])]
                else:
                    df = df[df[variable_name] == selected]
                
        except Exception as e:
            logger.error(f"Error in retrieve: {e}")
            logger.error(f"variable_filter: {variable_filter}")
            return None
        return df



class DistrictStatisticsService:
    def retrieve(
        self,
        container: Container,
        filtered_df: pd.DataFrame,
        # prediction_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        구별 평균 청구금액, 예측금액, 오차율 등을 계산
        """
        
        # 예측 데이터가 없는 경우 청구 데이터만으로 통계 계산
        # if prediction_df is None:
            # 구별 통계 계산 (예측 데이터 없이)
            # district_stats = filtered_df.groupby('district').agg({
            #     'price': ['mean', 'count'],
            # }).round(0)
            
            # # 컬럼명 정리
            # district_stats.columns = [
            #     'avg_claim_price',
            #     'claim_count',
            # ]
            # district_stats = district_stats.reset_index()
            
            # # 예측 데이터 관련 컬럼 추가 (더미 데이터)
            # district_stats['avg_predicted_price'] = district_stats['avg_claim_price']
            # district_stats['price_diff'] = 0
            # district_stats['error_rate'] = 0
            
            # return district_stats
        
        # 청구 데이터와 예측 데이터 병합
        # merged_df = pd.merge(
        #     filtered_df,
        #     prediction_df,
        #     on=["claim_id"],
        #     how="left"
        # )
        
        # 구별 통계 계산
        district_stats = filtered_df.groupby('district').agg({
            'price': ['mean', 'count'],
            # 'predicted_price': 'mean',
        }).round(0)
        
        # 컬럼명 정리
        district_stats.columns = [
            'avg_claim_price',
            'claim_count',
            # 'avg_predicted_price'
        ]
        district_stats = district_stats.reset_index()
        
        # # 오차 계산
        # district_stats['price_diff'] = district_stats['avg_predicted_price'] - district_stats['avg_claim_price']
        # district_stats['error_rate'] = (district_stats['price_diff'] / district_stats['avg_claim_price'] * 100).round(2)
        
        return district_stats

class PredictionStatisticsService:
    def retrieve(
        self,
        container: Container,
        variable_filter: List[str] = None,
    ) -> pd.DataFrame:
        df = container.prediction_df
        if variable_filter is not None:
            for variable_name, selected in variable_filter:
                logger.info(f"variable_name: {variable_name}, selected: {selected}")
                if selected == 'ALL':
                    continue
                if variable_name == 'age':
                    df = df[(df[variable_name] >= selected[0]) & (df[variable_name] <= selected[1])]
                else:
                    df = df[df[variable_name] == selected]
        return df


    def summarize_prediction(
        self,
        container: Container,
        insurance_claim_df: pd.DataFrame,
        prediction_df: pd.DataFrame,
    ) -> pd.DataFrame:
        '''
        드랍다운에 의한 filtering은 claim_price_df에서 이루어짐
        '''
        logger.info(
            f"""
prediction df
    df shape: {prediction_df.shape}
    df columns: {prediction_df.columns}
                """
        ) 
        claim_price_evaluation_df = pd.merge(
            insurance_claim_df,
            prediction_df,
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
                "district",
                "predicted_price",
                "diff",
                "error_rate",
            ]
        ]
        logger.info(
            f"""
    df shape: {claim_price_evaluation_df.shape}
    df columns: {claim_price_evaluation_df.columns}
"""
        )
        return claim_price_evaluation_df