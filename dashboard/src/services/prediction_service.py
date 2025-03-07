from typing import List, Tuple, Optional, Dict
import pandas as pd
import numpy as np
from models.container import Container
from utils.logger import get_logger

logger = get_logger(__name__)

class PredictionService:
    """예측 데이터 처리 서비스"""
    
    def retrieve(self, container: Container, variable_filter: List[Tuple[str, any]] = None) -> Optional[pd.DataFrame]:
        """필터링된 예측 데이터 조회"""
        if container.prediction_df is None:
            logger.warning("예측 데이터가 로드되지 않았습니다.")
            return None
            
        df = container.prediction_df.copy()
        
        if variable_filter is None:
            return df
            
        for variable_name, selected in variable_filter:
            logger.info(f"variable_name: {variable_name}, selected: {selected}")
            if selected == 'ALL':
                continue
                
            if variable_name == 'age':
                df = df[(df[variable_name] >= selected[0]) & (df[variable_name] <= selected[1])]
            else:
                # Enum 값을 문자열로 변환하여 비교
                if hasattr(selected, 'value'):
                    selected = selected.value
                df = df[df[variable_name] == selected]
                
        return df
        
    def summarize_prediction(self, container: Container, insurance_claim_df: pd.DataFrame, 
                            prediction_df: pd.DataFrame = None) -> pd.DataFrame:
        """예측 결과 요약"""
        if prediction_df is None:
            prediction_df = container.prediction_df
            
        if prediction_df is None:
            logger.error("예측 데이터가 없습니다.")
            return pd.DataFrame()
        
        # 실제 데이터와 예측 데이터 병합
        comparison_df = pd.merge(
            insurance_claim_df,
            prediction_df[['claim_id', 'predicted_price']],
            on='claim_id',
            how='inner'
        )
        
        # 차이 및 오차율 계산
        comparison_df['diff'] = comparison_df['predicted_price'] - comparison_df['price']
        comparison_df['error_rate'] = comparison_df['diff'] / comparison_df['price']
        
        # 필요한 컬럼만 선택
        result_df = comparison_df[[
            'claim_id', 'pet_id', 'breed', 'gender', 'neutralized', 
            'district', 'age', 'weight', 'price', 'issued_at',
            'predicted_price', 'diff', 'error_rate'
        ]]
        
        return result_df
        
    def calculate_model_metrics(self, df: pd.DataFrame) -> Dict:
        """모델 성능 지표 계산"""
        if df.empty:
            return {}
            
        avg_price = df['price'].mean()
        avg_pred = df['predicted_price'].mean()
        avg_diff = df['diff'].mean()
        avg_error = df['error_rate'].mean() * 100  # 백분율로 표시
        mse = (df['diff'] ** 2).mean()
        rmse = np.sqrt(mse)
        mae = df['diff'].abs().mean()
        
        return {
            'avg_price': avg_price,
            'avg_pred': avg_pred,
            'avg_diff': avg_diff,
            'avg_error': avg_error,
            'mse': mse,
            'rmse': rmse,
            'mae': mae
        }
        
    def analyze_by_category(self, df: pd.DataFrame, category: str) -> pd.DataFrame:
        """카테고리별 분석"""
        if df.empty:
            return pd.DataFrame()
            
        analysis = df.groupby(category).agg({
            'price': 'mean',
            'predicted_price': 'mean',
            'error_rate': ['mean', 'std', 'count']
        })
        
        analysis.columns = ['평균_실제가', '평균_예측가', '평균_오차율', '오차율_표준편차', '데이터_수']
        analysis['평균_오차율'] = analysis['평균_오차율'] * 100  # 백분율로 변환
        analysis['오차율_표준편차'] = analysis['오차율_표준편차'] * 100
        
        return analysis.reset_index()