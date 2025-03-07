from dataclasses import dataclass, field
from typing import Optional, Dict, List
import pandas as pd
from config.settings import Settings

@dataclass
class Container:
    """데이터 컨테이너 클래스"""
    settings: Settings = field(default_factory=Settings)
    insurance_claim_df: Optional[pd.DataFrame] = None
    prediction_df: Optional[pd.DataFrame] = None
    selected_date: Optional[str] = None
    available_dates: List[str] = field(default_factory=list)
    model_data: Dict[str, pd.DataFrame] = field(default_factory=dict)
    
    def set_insurance_claim_df(self, df: pd.DataFrame) -> None:
        """보험 청구 데이터 설정"""
        self.insurance_claim_df = df
    
    def set_prediction_df(self, df: pd.DataFrame) -> None:
        """예측 데이터 설정"""
        self.prediction_df = df
    
    def add_model_data(self, model_name: str, df: pd.DataFrame) -> None:
        """모델 데이터 추가"""
        self.model_data[model_name] = df
    
    def get_model_data(self, model_name: str) -> Optional[pd.DataFrame]:
        """모델 데이터 조회"""
        return self.model_data.get(model_name)
    
    def clear_model_data(self) -> None:
        """모델 데이터 초기화"""
        self.model_data.clear()