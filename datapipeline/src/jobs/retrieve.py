from datetime import date
import pandas as pd
import numpy as np

from typing import List, Optional, Tuple
from sklearn.model_selection import train_test_split

from src.dataset.data_manager import load_data
from src.dataset.schema import XY
from src.middleware.db_client import DBClient
from src.models.preprocess import DataPreprocessPipeline


class Retriever:

    def __init__(self, db_client: DBClient):
        self.db_client = db_client

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
#       
        generated_data = pd.read_csv('/data_storage/generated_insurance_claim.csv')
        generated_data.to_csv('/data_storage/insurance_claim.csv', index = False)
        
        
        return generated_data # load_data(self.db_client, sql_command, date_from, date_to) #

    def train_test_split(
        self,
        raw_df: pd.DataFrame,
        test_split_ratio: float,
        data_preprocess_pipeline: DataPreprocessPipeline,
    ) -> Tuple[XY, XY]:

        x = raw_df.drop(columns=["claim_price"])
        y = raw_df[["claim_price"]].astype(np.float64)

        preprocessed_x = data_preprocess_pipeline.preprocess(x)

        x_train, x_test, y_train, y_test = train_test_split(
            preprocessed_x, y, test_size=test_split_ratio, random_state=42
        )
        
        preprocessed_train_x = data_preprocess_pipeline.fit_transform(x_train)
        preprocessed_test_x = data_preprocess_pipeline.transform(x_test)
        
        # TODO: test_size config로 옮기기

        # x, y 나누기
        return XY(x=preprocessed_train_x, y=y_train), XY(x=preprocessed_test_x, y=y_test)
