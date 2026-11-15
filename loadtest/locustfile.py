"""Load test với endpoint POST /predict, gửi text đúng bài toán SMS spam/ham."""
import os,random
from locust import HttpUser,task,between
SAMPLES=[
 'Are we still meeting at 7 this evening?',
 'Please send me the report before tomorrow.',
 'Congratulations! You won free cash! Claim your prize now.',
 'URGENT winner! Reply YES for a free voucher.',
 'Can you send me the notes after the meeting?',
 'Free prize! Call now to claim your cash reward.'
]
class SMSUser(HttpUser):
 wait_time=between(1,3)
 @task
 def predict_sms(self):
  text=random.choice(SAMPLES)
  with self.client.post(os.getenv('API_PATH','/predict'),json={'text':text},name='POST /predict',timeout=15,catch_response=True) as response:
   if response.status_code!=200:
    response.failure(f'HTTP {response.status_code}: {response.text[:160]}');return
   try:
    data=response.json()
    if data.get('label') not in ('spam','ham') or not isinstance(data.get('confidence'),(int,float)):
     response.failure('Response thiếu label spam/ham hoặc confidence')
    elif data.get('history_saved') is not True: response.failure('History was not saved')
    elif not 0<=data['confidence']<=1: response.failure('confidence ngoài [0,1]')
    else:response.success()
   except ValueError:response.failure('Response không phải JSON')
