from abc import ABC, abstractmethod
from datetime import datetime

import os
from glob import glob

import pandas as pd

from src.middleware.logger import configure_logger


logger = configure_logger(__name__)

class AlertPolicy(ABC):
    @abstractmethod
    def analyze(self, df: pd.DataFrame) -> bool:
        raise NotImplementedError

class DataAmountAlertPolicy(AlertPolicy):
    def analyze(self, previous_df: pd.DataFrame, new_df: pd.DataFrame):
        # 전에 있던 정보들이 필요하다.
            
        prev_row_cnt, new_row_cnt = len(previous_df), len(new_df)
        logger.info(f"이전 데이터#: {prev_row_cnt}, 업데이트 데이터#: {new_row_cnt}")
        
        return (new_row_cnt - prev_row_cnt) >= 30
        

class Monitor:
    def __init__(self, pd_record_path: str, alert_policy: AlertPolicy):
        self.alert_policy = alert_policy
        self.pd_record_path = pd_record_path
        try:
            self.current_record = pd.read_csv(pd_record_path)
        except:
            logger.info("[비교대상 데이터 로컬에 없음]")
            self.current_record = None
    
    def alert(self, df: pd.DataFrame)-> bool:
        trigger_on = self.alert_policy.analyze(self.current_record, df)
        return trigger_on
        
    def update_record(self, df: pd.DataFrame):
        now = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        logger.info(f"[{now} 레코드 업데이트]")
        df.to_csv(self.pd_record_path, index = False)
        
        if self.current_record is None:
            self.current_record = pd.read_csv(self.pd_record_path)
    



