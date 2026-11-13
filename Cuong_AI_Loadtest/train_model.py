import json
from pathlib import Path
import joblib
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

root = Path(__file__).resolve().parent
iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(iris.data, iris.target, test_size=0.2, random_state=42, stratify=iris.target)
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=500, random_state=42))
model.fit(X_train, y_train)
pred = model.predict(X_test)
joblib.dump({'pipeline': model, 'labels': iris.target_names.tolist(), 'features': iris.feature_names}, root / 'iris_model.joblib')
metrics = {'accuracy': float(accuracy_score(y_test, pred)), 'test_samples': len(y_test), 'classification_report': classification_report(y_test, pred, target_names=iris.target_names, output_dict=True)}
(root / 'metrics.json').write_text(json.dumps(metrics, indent=2), encoding='utf-8')
print('Accuracy:', metrics['accuracy'])
