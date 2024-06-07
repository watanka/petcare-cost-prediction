import numpy as np

from locust import HttpUser, task, between, TaskSet
from datetime import datetime
import json
import logging

logging.basicConfig(level=logging.INFO)


class UserBehavior(TaskSet):
    # @task
    # def send_request_for_petcare_cost_prediction(self):
    #     user_id = 1
        
    #     json_dict = {'pet_breed_id': user_id,
    #             'birth': datetime.strptime('2024-03-27', "%Y-%M-%d").date(),
    #             'gender': '남자',
    #             'neuter_yn': 'y',
    #             'weight_kg': 10,
    #             'created_at': datetime.now().isoformat()
    #             }
        
    #     response = self.client.post('/predict', 
    #                                 data = json.dumps(json_dict, default = str, indent = 4)) 
        
    #     logging.info("Request to FastAPI server(include pre&post processing): "+ response.text)

    @task
    def send_request_for_overall_statistics(self):
        response = self.client.get('/statistics', params = {'breed_id': 1146})
        
        logging.info("Request to FastAPI server[get: /statistics] "+ response.text)
        


class LocustUser(HttpUser):
    host = 'http://localhost:8000'
    tasks = [UserBehavior]    