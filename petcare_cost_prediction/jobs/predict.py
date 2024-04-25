import pandas as pd
import numpy as np
from petcare_cost_prediction.models.preprocess import DataPreprocessPipeline


class Predictor(object):
    def filter(
        self,
        df: pd.DataFrame,
    ):
        print('filter the prediction')
        
        return df 
    
    
    def postprocess(self, df: pd.DataFrame, predictions: np.ndarray) -> pd.DataFrame:
        
        print('df에 prediction 추가')
        df['prediction'] = predictions
        
        return df
    
    def predict(
        self,
        model,
        data_preprocess_pipeline: DataPreprocessPipeline, 
        df : pd.DataFrame,
    ) -> pd.DataFrame:
        
        preprocessed_df = data_preprocess_pipeline.preprocess(df)
        x = data_preprocess_pipeline.transform(preprocessed_df)
        
        
        predictions = model.predict(x)
        
        integrated_result = self.postprocess(df = df, predictions = predictions)
        
        return integrated_result