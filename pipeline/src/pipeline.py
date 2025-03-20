from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler

from src.logger import get_logger

logger = get_logger("preprocess_pipeline")

class DataPreprocessPipeline:
    def __init__(self, config: Optional[Dict] = None):
        """
        데이터 전처리 파이프라인을 초기화합니다.
        
        Args:
            config (Dict): 전처리 설정
                {
                    "numeric": {
                        "handling": "standard_scale" | "minmax_scale" | "none",
                        "missing_value": "mean" | "median" | "zero" | "none"
                    },
                    "categorical": {
                        "handling": "one_hot" | "label" | "none",
                        "missing_value": "mode" | "unknown" | "none"
                    }
                }
        """
        self.config = self._get_default_config()
        if config:
            logger.info("사용자 정의 전처리 설정을 적용합니다.")
            self.config.update(config)
        
        logger.debug(f"전처리 설정: {self.config}")
        
        self.numeric_columns: List[str] = []
        self.categorical_columns: List[str] = []
        self.scalers: Dict[str, Union[StandardScaler, MinMaxScaler]] = {}
        self.categorical_mappings: Dict[str, Dict] = {}
        
    def _get_default_config(self) -> Dict:
        """기본 전처리 설정을 반환합니다."""
        return {
            "numeric": {
                "handling": "standard_scale",
                "missing_value": "mean"
            },
            "categorical": {
                "handling": "one_hot",
                "missing_value": "mode"
            }
        }
    
    def fit(self, df: pd.DataFrame, target_column: str = None):
        """
        데이터에 맞춰 전처리 파이프라인을 학습합니다.
        
        Args:
            df (pd.DataFrame): 학습 데이터
            target_column (str): 타겟 컬럼명
        """
        logger.info("전처리 파이프라인 학습을 시작합니다.")
        try:
            # 수치형/범주형 컬럼 구분
            self.numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            self.categorical_columns = df.select_dtypes(exclude=[np.number]).columns.tolist()
            
            if target_column:
                # 타겟 컬럼 제외
                if target_column in self.numeric_columns:
                    self.numeric_columns.remove(target_column)
                if target_column in self.categorical_columns:
                    self.categorical_columns.remove(target_column)
            
            logger.info(f"수치형 컬럼: {len(self.numeric_columns)}개")
            logger.info(f"범주형 컬럼: {len(self.categorical_columns)}개")
            
            # 수치형 컬럼 처리
            self._fit_numeric(df)
            
            # 범주형 컬럼 처리
            self._fit_categorical(df)
            
            logger.info("전처리 파이프라인 학습이 완료되었습니다.")
            
        except Exception as e:
            logger.error(f"전처리 파이프라인 학습 중 오류가 발생했습니다: {str(e)}", exc_info=True)
            raise
    
    def _fit_numeric(self, df: pd.DataFrame):
        """수치형 컬럼 전처리를 학습합니다."""
        if not self.numeric_columns:
            return
        
        numeric_config = self.config.get("numeric", {})
        handling = numeric_config.get("handling", "none")
        missing = numeric_config.get("missing_value", "none")
        
        logger.info(f"수치형 데이터 처리 방식: {handling}, 결측치 처리: {missing}")
        
        for col in self.numeric_columns:
            # 결측치 처리
            if missing == "mean":
                df[col].fillna(df[col].mean(), inplace=True)
            elif missing == "median":
                df[col].fillna(df[col].median(), inplace=True)
            elif missing == "zero":
                df[col].fillna(0, inplace=True)
            
            # 스케일링
            if handling == "standard_scale":
                scaler = StandardScaler()
                scaler.fit(df[[col]])
                self.scalers[col] = scaler
            elif handling == "minmax_scale":
                scaler = MinMaxScaler()
                scaler.fit(df[[col]])
                self.scalers[col] = scaler
    
    def _fit_categorical(self, df: pd.DataFrame):
        """범주형 컬럼 전처리를 학습합니다."""
        if not self.categorical_columns:
            return
        
        categorical_config = self.config.get("categorical", {})
        handling = categorical_config.get("handling", "none")
        missing = categorical_config.get("missing_value", "none")
        
        logger.info(f"범주형 데이터 처리 방식: {handling}, 결측치 처리: {missing}")
        
        for col in self.categorical_columns:
            # 결측치 처리
            if missing == "mode":
                mode_value = df[col].mode()[0]
                df[col].fillna(mode_value, inplace=True)
            elif missing == "unknown":
                df[col].fillna("unknown", inplace=True)
            
            # 인코딩
            if handling == "label":
                unique_values = df[col].unique()
                mapping = {val: idx for idx, val in enumerate(unique_values)}
                self.categorical_mappings[col] = mapping
            elif handling == "one_hot":
                unique_values = df[col].unique()
                mapping = {val: f"{col}_{val}" for val in unique_values}
                self.categorical_mappings[col] = mapping
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        데이터를 전처리합니다.
        
        Args:
            df (pd.DataFrame): 전처리할 데이터
            
        Returns:
            pd.DataFrame: 전처리된 데이터
        """
        logger.info("데이터 전처리를 시작합니다.")
        try:
            df = df.copy()
            
            # 수치형 컬럼 처리
            df = self._transform_numeric(df)
            
            # 범주형 컬럼 처리
            df = self._transform_categorical(df)
            
            logger.info("데이터 전처리가 완료되었습니다.")
            return df
            
        except Exception as e:
            logger.error(f"데이터 전처리 중 오류가 발생했습니다: {str(e)}", exc_info=True)
            raise
    
    def _transform_numeric(self, df: pd.DataFrame) -> pd.DataFrame:
        """수치형 컬럼을 전처리합니다."""
        if not self.numeric_columns:
            return df
        
        numeric_config = self.config.get("numeric", {})
        missing = numeric_config.get("missing_value", "none")
        
        for col in self.numeric_columns:
            if col not in df.columns:
                logger.warning(f"컬럼을 찾을 수 없습니다: {col}")
                continue
                
            # 결측치 처리
            if missing == "zero":
                df[col].fillna(0, inplace=True)
            
            # 스케일링
            if col in self.scalers:
                scaler = self.scalers[col]
                df[col] = scaler.transform(df[[col]])
        
        return df
    
    def _transform_categorical(self, df: pd.DataFrame) -> pd.DataFrame:
        """범주형 컬럼을 전처리합니다."""
        if not self.categorical_columns:
            return df
        
        categorical_config = self.config.get("categorical", {})
        handling = categorical_config.get("handling", "none")
        missing = categorical_config.get("missing_value", "none")
        
        for col in self.categorical_columns:
            if col not in df.columns:
                logger.warning(f"컬럼을 찾을 수 없습니다: {col}")
                continue
                
            # 결측치 처리
            if missing == "unknown":
                df[col].fillna("unknown", inplace=True)
            
            # 인코딩
            if handling == "label" and col in self.categorical_mappings:
                mapping = self.categorical_mappings[col]
                df[col] = df[col].map(mapping)
                # 새로운 카테고리에 대해서는 -1 할당
                df[col].fillna(-1, inplace=True)
            
            elif handling == "one_hot" and col in self.categorical_mappings:
                mapping = self.categorical_mappings[col]
                for val, new_col in mapping.items():
                    df[new_col] = (df[col] == val).astype(int)
                df.drop(col, axis=1, inplace=True)
        
        return df 