import json
import math
import re

from collections import Counter
from pathlib import Path


samples = {
    "positive": [
        "excellent product good quality love it",
        "great service friendly staff delicious food",
        "wonderful movie enjoyable story",
        "amazing phone works perfectly happy purchase",
    ],
    "negative": [
        "terrible product bad quality hate it",
        "awful service rude staff disgusting food",
        "boring movie disappointing story",
        "broken phone slow unhappy purchase",
    ],
}

counts = {
    label: Counter(
        re.findall(
            r"[a-z]+(?:'[a-z]+)?",
            " ".join(texts)
        )
    )
    for label, texts in samples.items()
}

vocabulary = set().union(
    *(set(words) for words in counts.values())
)

model = {
    "version": "demo-v1",
    "log_prior": {},
    "log_likelihood": {},
}

total_documents = sum(
    len(texts) for texts in samples.values()
)

for label, words in counts.items():
    model["log_prior"][label] = math.log(
        len(samples[label]) / total_documents
    )

    denominator = sum(words.values()) + len(vocabulary)

    model["log_likelihood"][label] = {
        word: math.log(
            (words[word] + 1) / denominator
        )
        for word in sorted(vocabulary)
    }

path = Path(__file__).with_name("model.json")

path.write_text(
    json.dumps(model, indent=2),
    encoding="utf-8"
)

print("Created demo model:", path)