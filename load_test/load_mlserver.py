import numpy as np

from locust import HttpUser, task, between, TaskSet
from datetime import datetime
import json
import logging

logging.basicConfig(level=logging.INFO)

test_sample = np.zeros((1, 15))

inference_request = {
        "inputs": [
            {
            "name": "",
            "shape": test_sample.shape,
            "datatype": "FP32",
            "data": test_sample.tolist()
            }
        ]
    }



class UserBehavior(TaskSet):
    @task
    def send_request_to_mlserver(self):
    
        response = self.client.post('/v2/models/light-gbm-regression/versions/v0.1.0/infer', 
                                json = inference_request) 
        logging.info("Request to mlserver : "+ response.text)

class LocustUser(HttpUser):
    host = 'http://localhost:8080'
    tasks = [UserBehavior]    