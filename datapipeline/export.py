import onnxmltools
import lightgbm as lgb
from src.models.light_gbm_regression import (
    LightGBMRegressionModel,
    LGB_REGRESSION_DEFAULT_PARAMS,
)

model_path = '../mlartifacts/light_gbm_regression_20240528_062443.txt'
output_path = 'light_gbm_regression.onnx'

model = LightGBMRegressionModel()

model.load(model_path)

lgb_model = model.model


onnx_model = onnxmltools.convert_lightgbm(lgb_model, initial_types=[(variable_name, data_type), (variable_name, data_type)])


onnxmltools.utils.save_model(onnx_model, output_path)