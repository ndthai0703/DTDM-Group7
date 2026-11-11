import base64
import json
import math
import os
import re
import time

from collections import Counter
from pathlib import Path


def load_model():
    bucket = os.environ.get("MODEL_BUCKET")

    if bucket:
        # Dùng khi triển khai AWS ở các ngày sau.
        import boto3

        path = Path("/tmp/sentiment-model.json")

        boto3.client("s3").download_file(
            bucket,
            os.environ["MODEL_KEY"],
            str(path)
        )

    else:
        # Dùng khi test local hôm nay.
        path = Path(
            os.environ.get(
                "MODEL_PATH",
                str(Path(__file__).with_name("model.json"))
            )
        )

    model = json.loads(
        path.read_text(encoding="utf-8")
    )

    print("[INIT] Model loaded:", model["version"])

    return model


# Nạp model ngoài handler.
# Chỉ chạy một lần khi execution environment khởi tạo.
MODEL = load_model()


def tokenize(text):
    return re.findall(
        r"[a-z]+(?:'[a-z]+)?",
        text.lower()
    )


def predict(text):
    words = Counter(tokenize(text))

    vocabulary = MODEL["log_likelihood"]["positive"]

    if not any(word in vocabulary for word in words):
        raise ValueError(
            "No supported model vocabulary found"
        )

    scores = {}

    for label in ("negative", "positive"):
        scores[label] = (
            MODEL["log_prior"][label]
            + sum(
                count
                * MODEL["log_likelihood"][label].get(
                    word, 0.0
                )
                for word, count in words.items()
            )
        )

    # Chuẩn hóa ổn định về số học.
    maximum = max(scores.values())

    weights = {
        label: math.exp(score - maximum)
        for label, score in scores.items()
    }

    label = max(weights, key=weights.get)

    confidence = (
        weights[label] / sum(weights.values())
    )

    return label, confidence


def response(code, data):
    return {
        "statusCode": code,
        "headers": {
            "Content-Type": "application/json; charset=utf-8"
        },
        "body": json.dumps(
            data,
            ensure_ascii=False
        ),
    }


def lambda_handler(event, context):
    started = time.perf_counter()

    method = (
        event.get("requestContext", {})
        .get("http", {})
        .get("method")
        or event.get("httpMethod", "POST")
    )

    if method != "POST":
        return response(
            405,
            {"error": "Only POST is supported"}
        )

    try:
        raw = event.get("body", "")

        if not isinstance(raw, str) or len(raw) > 20000:
            raise ValueError("Invalid request body")

        if event.get("isBase64Encoded"):
            raw = base64.b64decode(
                raw,
                validate=True
            ).decode("utf-8")

        data = json.loads(raw)

        if (
            not isinstance(data, dict)
            or not isinstance(data.get("text"), str)
        ):
            raise ValueError("text must be a string")

        text = data["text"].strip()

        if not 1 <= len(text) <= 2000 or not tokenize(text):
            raise ValueError(
                "Enter 1 to 2000 characters of English text"
            )

    except (ValueError, TypeError, UnicodeError) as error:
        return response(
            400,
            {"error": str(error)}
        )

    try:
        label, confidence = predict(text)

    except ValueError as error:
        return response(
            422,
            {"error": str(error)}
        )

    return response(
        200,
        {
            "label": label,
            "confidence": round(confidence, 6),
            "processing_ms": round(
                (time.perf_counter() - started) * 1000,
                3
            ),
            "model_version": MODEL["version"],
        }
    )