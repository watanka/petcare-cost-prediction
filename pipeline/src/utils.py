import pandas as pd
import numpy as np

from mlserver.rest.responses import Response

from src.dataset.schema import PetInfo, PetPredictResult
from src.preprocess import DataPreprocessPipeline

def preprocess_request_input(breeds_categories_used_in_train: list, data_preprocess_pipeline: DataPreprocessPipeline, input: PetInfo):
        df = pd.DataFrame([input.dict()])
        
        preprocessed_df = data_preprocess_pipeline.preprocess(df, breeds_categories_used_in_train)
        x = data_preprocess_pipeline.transform(preprocessed_df)
        
        return x
    
def convert_prediction_input(x: np.array):
    return {
        "inputs": [
            {
                "name": "pet_info",
                "shape": x.shape,
                "datatype": "FP32",
                "data": x.toarray().tolist()
            }
        ]
    }
    
def postprocess_output(input: PetInfo, prediction_response: Response) -> PetPredictResult:
    predicted_claim_price = [res['data'][0] for res in prediction_response.json()['outputs']][0] # batch or parallel model deployment will be different.
    age = input.created_at.date() - input.birth
    
    return PetPredictResult(
            pet_breed_id=input.pet_breed_id,
            age=age.days // 30 // 12,
            gender=input.gender,
            neuter_yn=input.neuter_yn,
            weight_kg=input.weight_kg,
            predicted_claim_price=round(predicted_claim_price/1000)* 1000)
    