import requests

import numpy as np


def test_send_request_to_mlserver():
    test_sample = np.zeros((1, 15))
    
    inference_request = {
            "inputs": [
                {
                "name": "predict-prob",
                "shape": test_sample.shape,
                "datatype": "FP32",
                "data": test_sample.tolist()
                }
            ]
        }

    endpoint = "http://localhost:8080/v2/models/light-gbm-regression/versions/v0.1.0/infer"
    response = requests.post(endpoint, json=inference_request)

    assert response.status_code == 200