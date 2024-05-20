from dataclasses import dataclass
from glob import glob
import os
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from src.models.base_model import BasePetCareCostPredictionModel
from src.models.light_gbm_regression import (
    LightGBMRegressionModel,
    LGB_REGRESSION_DEFAULT_PARAMS,
)


@dataclass(frozen=True)
class Model(object):
    name: str
    model: BasePetCareCostPredictionModel
    params: Dict


class MODELS(Enum):
    LIGHT_GBM_REGRESSION = Model(
        name="light_gbm_regression",
        model=LightGBMRegressionModel,
        params=LGB_REGRESSION_DEFAULT_PARAMS,
    )

    @staticmethod
    def has_value(name: str) -> bool:
        return name in [v.value.name for v in MODELS.__members__.values()]

    @staticmethod
    def get_list() -> List[Model]:
        return [v.value for v in MODELS.__members__.values()]

    @staticmethod
    def get_model(name: str) -> Optional[Model]:
        for model in [v.value for v in MODELS.__members__.values()]:
            if model.name == name:
                return model
        raise ValueError("cannot find the model")


def find_latest_file(folder_path, ext):
     # 최신 파일의 경로와 수정 시간을 저장할 변수를 초기화합니다.
    latest_file_path = None
    latest_modified_time = datetime.fromtimestamp(0)
    
    files = glob(os.path.join(folder_path, f'light_gbm_regression_*.{ext}' ))
    
    for file in files:
        modified_time = datetime.strptime(os.path.splitext(file.split('/')[-1].replace('light_gbm_regression_', ''))[0], "%Y%m%d_%H%M%S")
        
        if modified_time > latest_modified_time:
            latest_file_path = file
            latest_modified_time = modified_time
        
    return latest_file_path