import os
from locust import HttpUser, task, between

class PredictionUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def predict(self):
        payload = {'sepal_length': 5.1, 'sepal_width': 3.5, 'petal_length': 1.4, 'petal_width': 0.2}
        with self.client.post('/predict', json=payload, catch_response=True, name='POST /predict') as response:
            if response.status_code != 200:
                response.failure(f'HTTP {response.status_code}: {response.text[:150]}')
                return
            try:
                data = response.json()
                if not all(k in data for k in ('label', 'confidence')):
                    response.failure('Response missing label/confidence')
            except ValueError:
                response.failure('Response is not JSON')
