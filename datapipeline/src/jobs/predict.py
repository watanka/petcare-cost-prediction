import pandas as pd
import numpy as np
from src.models.preprocess import DataPreprocessPipeline
from src.middleware.logger import configure_logger

logger = configure_logger(__name__)

class Predictor(object):
    def filter(
        self,
        df: pd.DataFrame,
    ):
        print("filter the prediction")

        return df

    def postprocess(self, df: pd.DataFrame, predictions: np.ndarray) -> pd.DataFrame:
        df["prediction"] = predictions

        return df

    def predict(
        self,
        model,
        data_preprocess_pipeline: DataPreprocessPipeline,
        previous_df: pd.DataFrame,
        data_to_be_predicted_df: pd.DataFrame,
    ) -> pd.DataFrame:
        
    
        breeds = previous_df['pet_breed_id'].unique()
        logger.info(f"추론에 사용된 클래스 {breeds}")
        
        
        # df = pd.concat([previous_df, data_to_be_predicted_df])
        preprocessed_df = data_preprocess_pipeline.preprocess(data_to_be_predicted_df, breeds)
        # data_preprocess_pipeline.fit(df)
        x = data_preprocess_pipeline.transform(preprocessed_df)
        predictions = model.predict(x)
        
        return predictions[0]


    