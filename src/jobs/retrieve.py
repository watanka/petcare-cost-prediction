from datetime import date
import pandas as pd
import numpy as np

from typing import List, Optional, Tuple
from sklearn.model_selection import train_test_split

from src.dataset.data_manager import get_connection, load_data
from src.dataset.schema import XY
from src.models.preprocess import DataPreprocessPipeline

class Retriever:
    
    def __init__(self, url, user, password, name, port):
        self.conn = get_connection(url, user, password, name, port)
    
    
    def retrieve_dataset(
        self,
        sql_command: str,
        date_from: Optional[date],
        date_to: Optional[date],
        # item: str = "ALL",
        # store: str = "ALL"
    ) -> pd.DataFrame:
        
        # validation check
        # 데이터 컬럼 없을 때,
        # 데이터 row 없을 때,
        
        return load_data(self.conn, sql_command, date_from, date_to)
    
    
    def train_test_split(
        self,
        raw_df: pd.DataFrame,
        test_split_ratio: float,
        # 우리 데이터는 기간 상관없이 split한다.
        # train_year_and_week: YearAndWeek,
        # train_end_year_and_week: YearAndWeek,
        # test_year_and_week: YearAndWeek,
        data_preprocess_pipeline: DataPreprocessPipeline
    ) -> Tuple[XY, XY]:
        
        
        x = raw_df.drop(columns = ['claim_price'])
        y = raw_df[['claim_price']].astype(np.float64)
        
        preprocessed_x = data_preprocess_pipeline.preprocess(x)
        
        
        # TODO: test_size config로 옮기기
        x_train, x_test, y_train, y_test = train_test_split(preprocessed_x, y, test_size = test_split_ratio, random_state=42)
        
        
        # preprocessed_train_x = data_preprocess_pipeline.fit_transform(x_train)
        # preprocessed_test_x = data_preprocess_pipeline.transform(x_test)
        
        
        # x, y 나누기    
        return XY(x=x_train, y=y_train), XY(x=x_test, y=y_test)
    
    
        
        