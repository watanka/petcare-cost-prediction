from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from src.models.base_model import BasePetCareCostPredictionModel
from src.models.light_gbm_regression import LightGBMRegressionModel, LGB_REGRESSION_DEFAULT_PARAMS


@dataclass(frozen = True)
class Model(object):
    name: str
    model: BasePetCareCostPredictionModel
    params: Dict
    


class MODELS(Enum):
    LIGHT_GBM_REGRESSION = Model(
        name = "light_gbm_regression",
        model = LightGBMRegressionModel,
        params = LGB_REGRESSION_DEFAULT_PARAMS
    )
    
    @staticmethod
    def has_value(name: str) -> bool:
        return name in [v.value.name for v in MODELS.__members__.values()]
    

    @staticmethod
    def get_list() -> List[Model]:
        return [v.value for v in MODELS.__members__.values()]
    
    @staticmethod
    def get_model(name: str)-> Optional[Model]:
        for model in [v.value for v in MODELS.__members__.values()]:
            if model.name == name:
                return model
        raise ValueError('cannot find the model')