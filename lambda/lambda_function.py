# import base64
# import json
# import math
# import os
# import re
# import time
# import boto3
# import uuid

# from collections import Counter
# from pathlib import Path
# from datetime import datetime, timezone
# from decimal import Decimal

# def load_model():
#     bucket = os.environ.get("MODEL_BUCKET")

#     if bucket:
#         # Dùng khi triển khai AWS ở các ngày sau.
#         import boto3

#         path = Path("/tmp/sentiment-model.json")

#         boto3.client("s3").download_file(
#             bucket,
#             os.environ["MODEL_KEY"],
#             str(path)
#         )

#     else:
#         # Dùng khi test local hôm nay.
#         path = Path(
#             os.environ.get(
#                 "MODEL_PATH",
#                 str(Path(__file__).with_name("model.json"))
#             )
#         )

#     model = json.loads(
#         path.read_text(encoding="utf-8")
#     )

#     print("[INIT] Model loaded:", model["version"])

#     return model


# # Nạp model ngoài handler.
# # Chỉ chạy một lần khi execution environment khởi tạo.
# MODEL = load_model()


# def tokenize(text):
#     return re.findall(
#         r"[a-z]+(?:'[a-z]+)?",
#         text.lower()
#     )


# def predict(text):
#     words = Counter(tokenize(text))

#     vocabulary = MODEL["log_likelihood"]["positive"]

#     if not any(word in vocabulary for word in words):
#         raise ValueError(
#             "No supported model vocabulary found"
#         )

#     scores = {}

#     for label in ("negative", "positive"):
#         scores[label] = (
#             MODEL["log_prior"][label]
#             + sum(
#                 count
#                 * MODEL["log_likelihood"][label].get(
#                     word, 0.0
#                 )
#                 for word, count in words.items()
#             )
#         )

#     # Chuẩn hóa ổn định về số học.
#     maximum = max(scores.values())

#     weights = {
#         label: math.exp(score - maximum)
#         for label, score in scores.items()
#     }

#     label = max(weights, key=weights.get)

#     confidence = (
#         weights[label] / sum(weights.values())
#     )

#     return label, confidence


# def response(code, data):
#     return {
#         "statusCode": code,
#         "headers": {
#             "Content-Type": "application/json; charset=utf-8"
#         },
#         "body": json.dumps(
#             data,
#             ensure_ascii=False
#         ),
#     }


# def lambda_handler(event, context):
#     started = time.perf_counter()

#     method = (
#         event.get("requestContext", {})
#         .get("http", {})
#         .get("method")
#         or event.get("httpMethod", "POST")
#     )

#     if method != "POST":
#         return response(
#             405,
#             {"error": "Only POST is supported"}
#         )

#     try:
#         raw = event.get("body", "")

#         if not isinstance(raw, str) or len(raw) > 20000:
#             raise ValueError("Invalid request body")

#         if event.get("isBase64Encoded"):
#             raw = base64.b64decode(
#                 raw,
#                 validate=True
#             ).decode("utf-8")

#         data = json.loads(raw)

#         if (
#             not isinstance(data, dict)
#             or not isinstance(data.get("text"), str)
#         ):
#             raise ValueError("text must be a string")

#         text = data["text"].strip()

#         if not 1 <= len(text) <= 2000 or not tokenize(text):
#             raise ValueError(
#                 "Enter 1 to 2000 characters of English text"
#             )

#     except (ValueError, TypeError, UnicodeError) as error:
#         return response(
#             400,
#             {"error": str(error)}
#         )

#     try:
#         label, confidence = predict(text)

#     except ValueError as error:
#         return response(
#             422,
#             {"error": str(error)}
#         )

#     result = {
#         "label": label,
#         "confidence": round(confidence, 6),
#         "processing_ms": round(
#             (time.perf_counter() - started) * 1000,
#             3
#         ),
#         "model_version": MODEL["version"],
#     }

#     try:
#         metadata = save_history(text, result, context)

#     except Exception as error:
#         print(json.dumps({
#             "event": "history_write_failed",
#             "error_type": type(error).__name__,
#         }))

#         return response(
#             503,
#             {"error": "Could not save prediction history"}
#         )

#     result.update(metadata)
#     result["history_saved"] = True

#     result["handler_ms"] = round(
#         (time.perf_counter() - started) * 1000,
#         3
#     )

#     return response(200, result)


# HISTORY_TABLE_NAME = os.environ.get("HISTORY_TABLE")

# TABLE = (
#     boto3.resource("dynamodb").Table(HISTORY_TABLE_NAME)
#     if HISTORY_TABLE_NAME
#     else None
# )


# def save_history(text, result, context):
#     if TABLE is None:
#         raise RuntimeError("HISTORY_TABLE is not configured")

#     metadata = {
#         "id": (
#             getattr(context, "aws_request_id", None)
#             or str(uuid.uuid4())
#         ),
#         "timestamp": datetime.now(timezone.utc).isoformat(),
#     }

#     item = {
#         **metadata,
#         **result,
#         "text": text,
#     }

#     # DynamoDB cần Decimal thay cho float.
#     item = json.loads(
#         json.dumps(item),
#         parse_float=Decimal
#     )

#     TABLE.put_item(Item=item)

#     return metadata


"""Load the real spam model once; predict and persist history."""
import base64
import binascii
import json
import os
import time
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import boto3
from botocore.config import Config
from inference import load_model, predict

SDK_CONFIG = Config(connect_timeout=3, read_timeout=5,
                    retries={"mode": "standard", "total_max_attempts": 2})

def initialize_model():
    bucket = os.environ.get("MODEL_BUCKET")
    if bucket:
        key = os.environ.get("MODEL_KEY")
        if not key:
            raise RuntimeError("MODEL_KEY is required with MODEL_BUCKET")
        path = Path("/tmp/spam-model.json")
        boto3.client("s3", config=SDK_CONFIG).download_file(bucket, key, str(path))
    else:
        path = Path(os.environ.get("MODEL_PATH", str(
            Path(__file__).resolve().parents[1] / "model" / "artifacts" / "spam-v1.json")))
    return load_model(path)

# Initialized once per execution environment, outside the handler.
MODEL = initialize_model()
print(json.dumps({"event": "model_loaded", "model_version": MODEL["model_version"]}))
TABLE_NAME = os.environ.get("HISTORY_TABLE")
TABLE = (boto3.resource("dynamodb", config=SDK_CONFIG).Table(TABLE_NAME)
         if TABLE_NAME else None)
MAX_TEXT_LENGTH = 1000
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "")

def response(code, data):
    headers = {"Content-Type": "application/json; charset=utf-8"}
    if ALLOWED_ORIGIN:
        headers.update({"Access-Control-Allow-Origin": ALLOWED_ORIGIN,
                        "Access-Control-Allow-Methods": "POST,OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type"})
    return {"statusCode": code, "headers": headers,
            "body": json.dumps(data, ensure_ascii=False)}

def parse_input(event):
    raw = event.get("body", event)
    if isinstance(raw, str):
        if len(raw) > 20000:
            raise ValueError("Request body is too large")
        if event.get("isBase64Encoded"):
            raw = base64.b64decode(raw, validate=True).decode("utf-8")
        data = json.loads(raw)
    else:
        data = raw
    if not isinstance(data, dict) or not isinstance(data.get("text"), str):
        raise ValueError("text must be a string")
    text = data["text"].strip()
    if not 1 <= len(text) <= MAX_TEXT_LENGTH:
        raise ValueError("Enter 1 to 1000 characters of text")
    return text

def save_history(text, result, request_id):
    if TABLE is None:
        raise RuntimeError("HISTORY_TABLE is not configured")
    metadata = {"id": request_id, "timestamp": datetime.now(timezone.utc).isoformat()}
    item = {**metadata, **result, "text": text}
    TABLE.put_item(Item=json.loads(json.dumps(item), parse_float=Decimal))
    return metadata

def lambda_handler(event, context):
    started = time.perf_counter()
    request_id = getattr(context, "aws_request_id", None) or str(uuid.uuid4())
    if not isinstance(event, dict):
        return response(400, {"error": "Event must be an object", "request_id": request_id})
    method = (event.get("requestContext", {}).get("http", {}).get("method")
              or event.get("httpMethod", "POST")).upper()
    if method == "OPTIONS":
        return response(200, {})
    if method != "POST":
        return response(405, {"error": "Only POST is supported", "request_id": request_id})
    try:
        text = parse_input(event)
        result = predict(text, MODEL)
    except (ValueError, TypeError, UnicodeError, binascii.Error) as error:
        return response(400, {"error": str(error), "request_id": request_id})
    result["processing_time_ms"] = round((time.perf_counter() - started) * 1000, 3)
    try:
        result.update(save_history(text, result, request_id))
    except Exception as error:
        print(json.dumps({"event": "history_write_failed", "request_id": request_id,
                          "error_type": type(error).__name__}))
        return response(503, {"error": "Could not save prediction history",
                              "request_id": request_id})
    result["history_saved"] = True
    result["handler_ms"] = round((time.perf_counter() - started) * 1000, 3)
    print(json.dumps({"event": "prediction_completed", "request_id": request_id,
                      "label": result["label"], "handler_ms": result["handler_ms"]}))
    return response(200, result)
