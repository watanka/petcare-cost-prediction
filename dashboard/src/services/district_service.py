from typing import Optional
import pandas as pd
import geopandas as gpd
from models.container import Container
from utils.logger import get_logger

logger = get_logger(__name__)

class DistrictService:
    """지역 데이터 처리 서비스"""
    
    def retrieve(self, container: Container, filtered_df: pd.DataFrame, 
                prediction_df: pd.DataFrame = None) -> Optional[pd.DataFrame]:
        """구별 통계 데이터 조회"""
        if filtered_df is None or filtered_df.empty:
            logger.warning("필터링된 데이터가 없습니다.")
            return None
            
        # 예측 데이터가 없는 경우 청구 데이터만으로 통계 계산
        if prediction_df is None:
            # 구별 통계 계산 (예측 데이터 없이)
            district_stats = filtered_df.groupby('district').agg({
                'price': ['mean', 'count'],
            }).round(0)
            
            # 컬럼명 정리
            district_stats.columns = [
                'avg_claim_price',
                'claim_count',
            ]
            district_stats = district_stats.reset_index()
            
            # 예측 데이터 관련 컬럼 추가 (더미 데이터)
            district_stats['avg_predicted_price'] = district_stats['avg_claim_price']
            district_stats['price_diff'] = 0
            district_stats['error_rate'] = 0
            
            return district_stats
        
        # 청구 데이터와 예측 데이터 병합
        merged_df = pd.merge(
            filtered_df,
            prediction_df,
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
        
    def load_seoul_map(self, container: Container) -> Optional[gpd.GeoDataFrame]:
        """서울시 지도 데이터 로드"""
        try:
            # 서울시 구별 경계 shapefile 로드
            seoul_map = gpd.read_file(container.settings.seoul_shapefile, encoding='utf-8')
            return seoul_map
        except Exception as e:
            logger.error(f"서울시 지도 데이터 로드 중 오류 발생: {e}")
            return None