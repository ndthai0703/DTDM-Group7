"""Hàm tham khảo để tích hợp vào Lambda hiện hữu, không thay Lambda thật.
Model có thể đặt trong image tại /var/task/spam-v1.json hoặc mount từ /tmp.
"""
import json,os,time
from predict_local import load_model,predict
MODEL=load_model(os.getenv('MODEL_PATH',str(__import__('pathlib').Path(__file__).with_name('spam-v1.json'))))
def lambda_handler(event,context):
 start=time.perf_counter()
 try:
  body=event.get('body',event)
  if isinstance(body,str):body=json.loads(body)
  if not isinstance(body,dict):raise ValueError('Body cần là JSON object')
  text=body.get('text')
  result=predict(text,MODEL)
  result.pop('scores',None)
  result['processing_time_ms']=round((time.perf_counter()-start)*1000,3)
  # Chèn ghi DynamoDB ở đây bằng code hiện hữu của nhóm.
  return {'statusCode':200,'headers':{'Content-Type':'application/json','Access-Control-Allow-Origin':'*'},'body':json.dumps(result,ensure_ascii=False)}
 except (ValueError,TypeError,json.JSONDecodeError) as e:
  return {'statusCode':400,'headers':{'Content-Type':'application/json','Access-Control-Allow-Origin':'*'},'body':json.dumps({'error':str(e)},ensure_ascii=False)}
