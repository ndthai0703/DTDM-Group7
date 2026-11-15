# """Huấn luyện Multinomial Naive Bayes, xuất JSON triển khai không cần sklearn."""
# import argparse,csv,json,math,re
# from collections import Counter
# from pathlib import Path
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import classification_report,confusion_matrix,accuracy_score,precision_recall_fscore_support
# BASE=Path(__file__).resolve().parent
# TOKEN_REGEX=r"(?u)\b\w\w+\b"
# def tokens(text):return re.findall(TOKEN_REGEX,text.lower())
# def fit(rows,alpha=1.0):
#  labels=['ham','spam']; doc_counts=Counter(y for y,x in rows); cnt={k:Counter() for k in labels}
#  for y,x in rows:cnt[y].update(tokens(x))
#  vocab=sorted(set(cnt['ham'])|set(cnt['spam'])); V=len(vocab)
#  result={'schema_version':'sms-spam-nb-v1','model_version':'spam-v1','task':'sms_spam_classification','algorithm':'multinomial_naive_bayes','labels':labels,'tokenizer':{'lowercase':True,'pattern':TOKEN_REGEX},'class_log_prior':{c:math.log(doc_counts[c]/len(rows)) for c in labels},'feature_log_prob':{},'unknown_log_prob':{},'training':{'samples':len(rows),'class_counts':dict(doc_counts),'alpha':alpha}}
#  for c in labels:
#   denom=sum(cnt[c].values())+alpha*V
#   result['feature_log_prob'][c]={w:round(math.log((cnt[c][w]+alpha)/denom),9) for w in vocab}
#   result['unknown_log_prob'][c]=round(math.log(alpha/denom),9)
#  return result

# def main():
#  ap=argparse.ArgumentParser();ap.add_argument('--data',default=str(BASE/'data/demo_sms_labeled.csv'));ap.add_argument('--output',default=str(BASE/'spam-v1.json'));args=ap.parse_args()
#  with open(args.data,encoding='utf-8-sig',newline='') as f:
#   reader=csv.DictReader(f);rows=[(r['label'].strip().lower(),r['text'].strip()) for r in reader if r['label'].strip() and r['text'].strip()]
#  assert set(y for y,x in rows)=={'ham','spam'},'Nhãn chỉ được là ham/spam'
#  train,test=train_test_split(rows,test_size=0.2,random_state=42,stratify=[y for y,x in rows])
#  model=fit(train)
#  Path(args.output).write_text(json.dumps(model,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
#  from predict_local import predict
#  pred=[predict(x,model)['label'] for y,x in test];truth=[y for y,x in test]
#  pr,rec,f1,_=precision_recall_fscore_support(truth,pred,labels=['spam'],zero_division=0)
#  metrics={'data_source':str(Path(args.data).name),'dataset_total':len(rows),'train_samples':len(train),'test_samples':len(test),'accuracy':accuracy_score(truth,pred),'spam_precision':float(pr[0]),'spam_recall':float(rec[0]),'spam_f1':float(f1[0]),'confusion_matrix_labels':['ham','spam'],'confusion_matrix':confusion_matrix(truth,pred,labels=['ham','spam']).tolist(),'classification_report':classification_report(truth,pred,labels=['ham','spam'],output_dict=True,zero_division=0),'note':'Chỉ số trên tập thử demo tự soạn; không phải chất lượng UCI/AWS.'}
#  (BASE/'results'/'local_metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2),encoding='utf-8')
#  print(json.dumps({k:v for k,v in metrics.items() if k!='classification_report'},indent=2,ensure_ascii=False))
# if __name__=='__main__':main()

"""Huấn luyện Multinomial Naive Bayes, xuất JSON triển khai không cần sklearn."""
import argparse,csv,json,math,re
from collections import Counter
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report,confusion_matrix,accuracy_score,precision_recall_fscore_support
BASE=Path(__file__).resolve().parent
TOKEN_REGEX=r"(?u)\b\w\w+\b"
def tokens(text):return re.findall(TOKEN_REGEX,text.lower())
def fit(rows,alpha=1.0):
 labels=['ham','spam']; doc_counts=Counter(y for y,x in rows); cnt={k:Counter() for k in labels}
 for y,x in rows:cnt[y].update(tokens(x))
 vocab=sorted(set(cnt['ham'])|set(cnt['spam'])); V=len(vocab)
 result={'schema_version':'sms-spam-nb-v1','model_version':'spam-v1','task':'sms_spam_classification','algorithm':'multinomial_naive_bayes','labels':labels,'tokenizer':{'lowercase':True,'pattern':TOKEN_REGEX},'class_log_prior':{c:math.log(doc_counts[c]/len(rows)) for c in labels},'feature_log_prob':{},'unknown_log_prob':{},'training':{'samples':len(rows),'class_counts':dict(doc_counts),'alpha':alpha}}
 for c in labels:
  denom=sum(cnt[c].values())+alpha*V
  result['feature_log_prob'][c]={w:round(math.log((cnt[c][w]+alpha)/denom),9) for w in vocab}
  result['unknown_log_prob'][c]=round(math.log(alpha/denom),9)
 return result

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--data',default=str(BASE/'data/demo_sms_labeled.csv'));ap.add_argument('--output',default=str(BASE/'artifacts'/'spam-v1.json'));args=ap.parse_args()
 with open(args.data,encoding='utf-8-sig',newline='') as f:
  reader=csv.DictReader(f);rows=[(r['label'].strip().lower(),r['text'].strip()) for r in reader if r['label'].strip() and r['text'].strip()]
 assert set(y for y,x in rows)=={'ham','spam'},'Nhãn chỉ được là ham/spam'
 train,test=train_test_split(rows,test_size=0.2,random_state=42,stratify=[y for y,x in rows])
 model=fit(train)
 Path(args.output).parent.mkdir(parents=True,exist_ok=True)
 (BASE/'results').mkdir(parents=True,exist_ok=True)
 Path(args.output).write_text(json.dumps(model,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 from predict_local import predict
 pred=[predict(x,model)['label'] for y,x in test];truth=[y for y,x in test]
 pr,rec,f1,_=precision_recall_fscore_support(truth,pred,labels=['spam'],zero_division=0)
 metrics={'data_source':str(Path(args.data).name),'dataset_total':len(rows),'train_samples':len(train),'test_samples':len(test),'accuracy':accuracy_score(truth,pred),'spam_precision':float(pr[0]),'spam_recall':float(rec[0]),'spam_f1':float(f1[0]),'confusion_matrix_labels':['ham','spam'],'confusion_matrix':confusion_matrix(truth,pred,labels=['ham','spam']).tolist(),'classification_report':classification_report(truth,pred,labels=['ham','spam'],output_dict=True,zero_division=0),'note':'Chỉ số trên tập thử demo tự soạn; không phải chất lượng UCI/AWS.'}
 (BASE/'results'/'local_metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({k:v for k,v in metrics.items() if k!='classification_report'},indent=2,ensure_ascii=False))
if __name__=='__main__':main()
