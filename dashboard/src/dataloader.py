
import pandas as pd
from configurations import Configurations
from logger import configure_logger

logger = configure_logger(__name__)

class DataLoader():
    def __init__(self, config: Configurations):
        self.config = config
    
    def init_df(self):
        insurance_claim_df = self.load_df(file_path=self.config.insurance_claim_record_file)
        prediction_df = self.load_df(file_path=self.config.insurance_claim_prediction_file)
        
        return insurance_claim_df, prediction_df

    def load_df(
        self,
        file_path: str,
    ) -> pd.DataFrame:
        logger.info(f"read {file_path}")
        df = pd.read_csv(file_path)
        
        # if 'age' not in df.columns:
        #     df['age'] = (pd.to_datetime(df['created_at']) - pd.to_datetime(df['birth'])).dt.days
        
        logger.info(
            f"""
read {file_path}
shape: {df.shape}
columns: {df.columns}
        """
        )
        return df

    def load_insurance_claim_df(
        self,
        file_path: str,
    ):
        self.insurance_claim_df = self.load_df(file_path=file_path)
        # self.insurance_claim_df["date"] = pd.to_datetime(self.insurance_claim_df["updated_at"])
        # self.insurance_claim_df["year"] = self.insurance_claim_df.date.dt.year
        #TODO: validation
        logger.info(
            f"""
formatted {file_path}
shape: {self.insurance_claim_df.shape}
columns: {self.insurance_claim_df.columns}
        """
        )

    def load_prediction_df(
        self,
        prediction_file_path: str,
    ):
        self.prediction_df = self.load_df(file_path=prediction_file_path)
        # TODO: validation
        logger.info(
            f"""
formatted {prediction_file_path}
shape: {self.prediction_df.shape}
columns: {self.prediction_df.columns}
        """
        )
