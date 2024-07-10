import os
from datetime import datetime
import glob
import pandas as pd
import numpy as np

from mlserver.rest.responses import Response

from schema import PetInfo, PetPredictResult
from preprocess import DataPreprocessPipeline



def preprocess_request_input(breeds_categories_used_in_train: list, data_preprocess_pipeline: DataPreprocessPipeline, input: PetInfo):
        df = pd.DataFrame([input.dict()])
        
        preprocessed_df = data_preprocess_pipeline.preprocess(df, breeds_categories_used_in_train)
        x = data_preprocess_pipeline.transform(preprocessed_df)
        
        return x
    
def convert_prediction_input(x):
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
    

def glob_recursive(dirname, pattern):
    matches = []
    for root, dirs, files in os.walk(dirname):  # 현재 디렉토리부터 시작하여 모든 하위 폴더를 순회
        for name in files + dirs:  # 현재 디렉토리의 파일과 하위 디렉토리들을 모두 고려
            full_path = os.path.join(root, name)
            if glob.fnmatch.fnmatch(full_path, pattern):  # 파일 또는 폴더의 경로가 패턴과 일치하는지 확인
                matches.append(full_path)
    return matches
    

    
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
    

def find_latest_file(folder_path, ext):
     # 최신 파일의 경로와 수정 시간을 저장할 변수를 초기화합니다.
    latest_file_path = None
    latest_modified_time = datetime.fromtimestamp(0)
    
    files = glob_recursive(folder_path, f'*light_gbm_regression_*.{ext}' )

    for file in files:
        modified_time = datetime.strptime(os.path.splitext(file.split('/')[-1].replace('light_gbm_regression_', ''))[0], "%Y%m%d_%H%M%S")
        
        if modified_time > latest_modified_time:
            latest_file_path = file
            latest_modified_time = modified_time
        
    return latest_file_path