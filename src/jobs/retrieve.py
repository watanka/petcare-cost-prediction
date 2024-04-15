from datetime import date
import pandas as pd
from typing import List, Optional, Tuple

from src.dataset.data_manager import get_connection, load_data
from src.dataset.schema import YearAndWeek, XY
from src.models.preprocess import DataPreprocessPipeline

class Retriever:
    
    def __init__(self, db_host, db_user, db_password, db_name, db_port):
        self.conn = get_connection(db_host, db_user, db_password, db_name, db_port)
    
    
    def retrieve_dataset(
        self,
        sql_command: str,
        date_from: Optional[date],
        date_to: Optional[date],
        item: str = "ALL",
        store: str = "ALL"
    ) -> pd.DataFrame:
        
        # validation check
        # 데이터 컬럼 없을 때,
        # 데이터 row 없을 때,
        
        return load_data(self.conn, sql_command)
    
    
    def train_test_split(
        self,
        raw_df: pd.DataFrame,
        train_year_and_week: YearAndWeek,
        train_end_year_and_week: YearAndWeek,
        test_year_and_week: YearAndWeek,
        data_preprocess_pipeline: DataPreprocessPipeline
    ) -> Tuple[XY, XY]:
        
        df = data_preprocess_pipeline.preprocess(raw_df)
        
        
        
        def split():
            return pd.DataFrame.from_dict({"train_attribute": "dummy"}), pd.DataFrame.from_dict({"claim_price": "dummy"})
        
        train_df, test_df = split(df, train_year_and_week, train_end_year_and_week, test_year_and_week)
        
        
        preprocessed_train_df = data_preprocess_pipeline.fit_transform(x = train_df)
        preprocessed_test_df = data_preprocess_pipeline.transfrom(test_df)
        
        
        # x, y 나누기
        x_train = (preprocessed_train_df[data_preprocess_pipeline.preprocessed_columns]
                    .drop(['claim_price'], axis = 1)
                    .reset_index(drop = True)
        ) 
                    
        y_train = preprocessed_train_df[['claim_price']].reset_index(drop = True)
        
        x_test = (preprocessed_test_df[data_preprocess_pipeline.preprocessed_columns]
                    .drop(['claim_price'], axis = 1)
                    .reset_index(drop = True)
        ) 
                    
        y_test = preprocessed_test_df[['claim_price']].reset_index(drop = True)
    
    
        return XY(x=x_train, y=y_train), XY(x=x_test, y=y_test)
    
    
        
        