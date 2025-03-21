from dataclasses import dataclass
import glob
import os
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from src.models.base_model import BasePetCareCostPredictionModel
from src.models.light_gbm_regression import (
    LightGBMRegressionModelServing,
)


@dataclass(frozen=True)
class Model(object):
    model_name: str
    model: BasePetCareCostPredictionModel
    params: Dict


class MODELS(Enum):
    LIGHT_GBM_REGRESSION = Model(
        model_name="light_gbm_regression_serving",
        model=LightGBMRegressionModelServing,
        params=None,
    )

    @staticmethod
    def has_value(name: str) -> bool:
        return name in [v.value.model_name for v in MODELS.__members__.values()]

    @staticmethod
    def get_list() -> List[Model]:
        return [v.value for v in MODELS.__members__.values()]

    @staticmethod
    def get_model(name: str, params: Optional[Dict] = None) -> Optional[Model]:
        for model in [v.value for v in MODELS.__members__.values()]:
            if model.model_name == name:
                return model
        raise ValueError(f"cannot find the model {name}")

    
    

def glob_recursive(dirname, pattern):
    matches = []
    for root, dirs, files in os.walk(dirname):  
        for name in files + dirs: 
            full_path = os.path.join(root, name)
            if glob.fnmatch.fnmatch(full_path, pattern):
                matches.append(full_path)
    return matches



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