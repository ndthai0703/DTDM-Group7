# """Pure Python JSON inference: có thể dùng trực tiếp trong AWS Lambda."""
# import json,math,re
# from pathlib import Path
# ROOT=Path(__file__).resolve().parent

# def load_model(path=ROOT/'spam-v1.json'):
#  with open(path,encoding='utf-8') as f:model=json.load(f)
#  if model.get('schema_version')!='sms-spam-nb-v1' or model.get('labels')!=['ham','spam']:
#   raise ValueError('Model JSON không đúng schema sms-spam-nb-v1')
#  return model

# def predict(text,model):
#  if not isinstance(text,str) or not text.strip():raise ValueError('text phải là chuỗi không rỗng')
#  pattern=model['tokenizer']['pattern'];words=re.findall(pattern,text.lower())
#  count={w:words.count(w) for w in set(words)}
#  logs={}
#  for label in model['labels']:
#   weights=model['feature_log_prob'][label];missing=model['unknown_log_prob'][label]
#   logs[label]=model['class_log_prior'][label]+sum(n*weights.get(w,missing) for w,n in count.items())
#  mx=max(logs.values());exp={k:math.exp(v-mx) for k,v in logs.items()};z=sum(exp.values());probs={k:exp[k]/z for k in exp}
#  label=max(probs,key=probs.get)
#  return {'label':label,'confidence':round(probs[label],6),'scores':{k:round(v,6) for k,v in probs.items()},'model_version':model['model_version']}

# if __name__=='__main__':
#  import sys
#  model=load_model();text=' '.join(sys.argv[1:]) or 'Congratulations! You won a free cash prize. Claim now!'
#  print(json.dumps(predict(text,model),ensure_ascii=False,indent=2))

"""Use the same inference implementation as Lambda."""
import argparse
import json
import sys
from pathlib import Path
BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE.parent / "lambda"))
from inference import load_model, predict

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("text", nargs="+", help="SMS text")
    parser.add_argument("--model", default=str(BASE / "artifacts" / "spam-v1.json"))
    args = parser.parse_args()
    print(json.dumps(predict(" ".join(args.text), load_model(args.model)), indent=2))
