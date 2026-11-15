"""Pure Python inference for the supplied sms-spam-nb-v1 model."""
import json
import math
import re
from collections import Counter
from pathlib import Path

def load_model(path):
    model = json.loads(Path(path).read_text(encoding="utf-8"))
    if model.get("schema_version") != "sms-spam-nb-v1" or model.get("labels") != ["ham", "spam"]:
        raise ValueError("Expected sms-spam-nb-v1 model with ham/spam labels")
    re.compile(model["tokenizer"]["pattern"])
    for label in model["labels"]:
        if not math.isfinite(model["class_log_prior"][label]):
            raise ValueError("Invalid class prior")
        if not math.isfinite(model["unknown_log_prob"][label]):
            raise ValueError("Invalid unknown-token probability")
        if not model["feature_log_prob"][label]:
            raise ValueError("Empty model vocabulary")
    return model

def predict(text, model):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("text must be a non-empty string")
    normalized = text.lower() if model["tokenizer"].get("lowercase", True) else text
    words = Counter(re.findall(model["tokenizer"]["pattern"], normalized))
    if not words:
        raise ValueError("Enter text containing words")
    scores = {}
    for label in model["labels"]:
        weights = model["feature_log_prob"][label]
        scores[label] = model["class_log_prior"][label] + sum(
            count * weights.get(word, model["unknown_log_prob"][label])
            for word, count in words.items()
        )
    maximum = max(scores.values())
    weights = {label: math.exp(score - maximum) for label, score in scores.items()}
    total = sum(weights.values())
    label = max(weights, key=weights.get)
    return {"label": label, "confidence": round(weights[label] / total, 6),
            "model_version": model["model_version"]}
