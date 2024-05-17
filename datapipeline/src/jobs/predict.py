import pandas as pd
import numpy as np
from src.models.preprocess import DataPreprocessPipeline


class Predictor(object):
    def filter(
        self,
        df: pd.DataFrame,
    ):
        print("filter the prediction")

        return df

    def postprocess(self, df: pd.DataFrame, predictions: np.ndarray) -> pd.DataFrame:

        print("df에 prediction 추가")
        df["prediction"] = predictions

        return df

    def predict(
        self,
        model,
        data_preprocess_pipeline: DataPreprocessPipeline,
        previous_df: pd.DataFrame,
        data_to_be_predicted_df: pd.DataFrame,
    ) -> pd.DataFrame:
        df = pd.concat([previous_df, data_to_be_predicted_df])
        print("df : ", df)
        preprocessed_df = data_preprocess_pipeline.preprocess(df)
        print('preprocessed_df : ', preprocessed_df)
        data_preprocess_pipeline.fit(df)
        x = data_preprocess_pipeline.transform(preprocessed_df)
        
        print("x: ", x)

        predictions = model.predict(x)

        ## TODO: 다시 추론 결괏값만 분리
        integrated_result = self.postprocess(df=df, predictions=predictions)

        return integrated_result


    