from typing import List, Tuple, Optional
import pandas as pd
from models.container import Container
from utils.logger import get_logger

logger = get_logger(__name__)

class DataService:
    """데이터 처리 기본 서비스"""
    
    def retrieve(self, container: Container, variable_filter: List[Tuple[str, any]] = None) -> Optional[pd.DataFrame]:
        """필터링된 데이터 조회"""
        if container.insurance_claim_df is None:
            logger.warning("보험 청구 데이터가 로드되지 않았습니다.")
            return None
            
        df = container.insurance_claim_df.copy()
        
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
        
    def get_unique_values(self, container: Container, column_name: str) -> List:
        """특정 컬럼의 고유값 목록 조회"""
        if container.insurance_claim_df is None:
            logger.warning("보험 청구 데이터가 로드되지 않았습니다.")
            return []
            
        return container.insurance_claim_df[column_name].unique().tolist()
        
    def get_value_range(self, container: Container, column_name: str) -> Tuple[float, float]:
        """특정 컬럼의 값 범위 조회"""
        if container.insurance_claim_df is None:
            logger.warning("보험 청구 데이터가 로드되지 않았습니다.")
            return (0, 0)
            
        return (
            container.insurance_claim_df[column_name].min(),
            container.insurance_claim_df[column_name].max()
        )
        
    def get_summary_statistics(self, df: pd.DataFrame) -> pd.DataFrame:
        """요약 통계 계산"""
        if df is None or df.empty:
            logger.warning("요약 통계를 계산할 데이터가 없습니다.")
            return pd.DataFrame()
            
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        summary = df[numeric_cols].describe().T
        
        # 추가 통계량 계산
        summary['median'] = df[numeric_cols].median()
        summary['mode'] = df[numeric_cols].mode().iloc[0]
        summary['missing'] = df[numeric_cols].isna().sum()
        summary['missing_pct'] = (df[numeric_cols].isna().sum() / len(df)) * 100
        
        return summary