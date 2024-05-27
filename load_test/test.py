from locust import HttpUser, task, between, TaskSet
from datetime import datetime
import json
import logging

logging.basicConfig(level=logging.INFO)

class UserBehavior(TaskSet):
    @task
    def predict_petcare_price(self):
        user_id = 1
        
        json_dict = {'pet_breed_id': user_id,
                'birth': datetime.strptime('2024-03-27', "%Y-%M-%d").date(),
                'gender': '남자',
                'neuter_yn': 'y',
                'weight_kg': 10,
                'created_at': datetime.now().isoformat()
                
                }
        
        response = self.client.post('/predict', data = json.dumps(json_dict, default = str, indent = 4)) 
        
        logging.info(response.text)


class LocustUser(HttpUser):
    host = 'http://localhost:8000'
    tasks = [UserBehavior]    