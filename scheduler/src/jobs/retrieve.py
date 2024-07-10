from datetime import date
import pandas as pd

from typing import Optional

from src.dataset.data_manager import load_data
from src.middleware.db_client import DBClient
from src.middleware.logger import configure_logger

logger = configure_logger(__name__)

class Retriever:

    def __init__(self, db_client: DBClient):
        self.db_client = db_client

    def retrieve_dataset(
        self,
        sql_command: str,
        date_from: Optional[date]=None,
        date_to: Optional[date]=None,
        # item: str = "ALL",
        # store: str = "ALL"
    ) -> pd.DataFrame:

        # validation check
        # 데이터 컬럼 없을 때,
        # 데이터 row 없을 때,
#       
        # generated_data = pd.read_csv('../data_storage/generated_insurance_claim.csv') ## TODO
        # generated_data.to_csv('../data_storage/insurance_claim.csv', index = False)
        
        
        # TODO: DB VPC 설정 확인
        return load_data(self.db_client, sql_command)