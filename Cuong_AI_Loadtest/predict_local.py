import json
from pathlib import Path
import joblib

bundle = joblib.load(Path(__file__).resolve().parent / 'iris_model.joblib')

def predict(payload):
    values = [payload[k] for k in ('sepal_length', 'sepal_width', 'petal_length', 'petal_width')]
    if any(not isinstance(v, (int, float)) or isinstance(v, bool) or not 0 < v < 20 for v in values):
        raise ValueError('Each feature must be a numeric value between 0 and 20')
    probs = bundle['pipeline'].predict_proba([values])[0]
    idx = int(probs.argmax())
    return {'label': bundle['labels'][idx], 'confidence': round(float(probs[idx]), 4)}

if __name__ == '__main__':
    print(json.dumps(predict({'sepal_length': 5.1, 'sepal_width': 3.5, 'petal_length': 1.4, 'petal_width': 0.2}), indent=2))
