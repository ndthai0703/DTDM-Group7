import base64
import importlib
import json
import os
import sys
import unittest
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lambda"))
os.environ.pop("MODEL_BUCKET", None)
os.environ.pop("HISTORY_TABLE", None)
os.environ["MODEL_PATH"] = str(ROOT / "model" / "artifacts" / "spam-v1.json")
import lambda_function as app

class HandlerTests(unittest.TestCase):
    def setUp(self):
        self.table = MagicMock()
        self.patch = patch.object(app, "TABLE", self.table)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def invoke(self, text, **extra):
        event = {"httpMethod": "POST", "body": json.dumps({"text": text}), **extra}
        response = app.lambda_handler(event, SimpleNamespace(aws_request_id="test-request"))
        return response["statusCode"], json.loads(response["body"])

    def test_spam_and_saved_decimal(self):
        code, data = self.invoke("Congratulations! You won free cash! Claim your prize now.")
        self.assertEqual(code, 200)
        self.assertEqual(data["label"], "spam")
        self.assertTrue(data["history_saved"])
        self.assertEqual(data["model_version"], "spam-v1")
        self.assertGreaterEqual(data["processing_time_ms"], 0)
        self.assertTrue(0 <= data["confidence"] <= 1)
        item = self.table.put_item.call_args.kwargs["Item"]
        self.assertIsInstance(item["confidence"], Decimal)
        self.assertEqual(item["id"], "test-request")

    def test_ham(self):
        self.assertEqual(self.invoke("Please send me the report before tomorrow.")[1]["label"], "ham")

    def test_invalid_inputs_do_not_write(self):
        for value in ["", "  ", 123, None, "x" * 1001, "!!!"]:
            with self.subTest(value=str(value)[:20]):
                self.assertEqual(self.invoke(value)[0], 400)
        self.table.put_item.assert_not_called()

    def test_invalid_json(self):
        self.assertEqual(app.lambda_handler({"body": "{"}, None)["statusCode"], 400)

    def test_json_array(self):
        self.assertEqual(app.lambda_handler({"body": "[]"}, None)["statusCode"], 400)

    def test_base64_and_http_api_v2(self):
        raw = base64.b64encode(json.dumps({"text": "Please send me the report before tomorrow."}).encode()).decode()
        event = {"requestContext": {"http": {"method": "POST"}}, "isBase64Encoded": True, "body": raw}
        self.assertEqual(app.lambda_handler(event, None)["statusCode"], 200)

    def test_invalid_base64(self):
        self.assertEqual(app.lambda_handler({"body": "%%%", "isBase64Encoded": True}, None)["statusCode"], 400)

    def test_direct_console_event(self):
        self.assertEqual(app.lambda_handler({"text": "Please send me the report before tomorrow."}, None)["statusCode"], 200)

    def test_method_and_preflight(self):
        self.assertEqual(self.invoke("hello", httpMethod="GET")[0], 405)
        self.assertEqual(self.invoke("hello", httpMethod="OPTIONS")[0], 200)
        self.table.put_item.assert_not_called()

    def test_db_failure_is_503(self):
        self.table.put_item.side_effect = RuntimeError("db unavailable")
        code, body = self.invoke("Please send me the report before tomorrow.")
        self.assertEqual(code, 503)
        self.assertNotIn("history_saved", body)

    def test_missing_table_is_503(self):
        with patch.object(app, "TABLE", None):
            self.assertEqual(self.invoke("Please send the report")[0], 503)

    def test_model_not_reloaded_during_invocations(self):
        with patch.object(app, "initialize_model") as loader:
            self.invoke("Send me the report")
            self.invoke("Free prize claim now")
            loader.assert_not_called()

    def test_s3_init_uses_bucket_key_and_model(self):
        original = app.MODEL
        def download(bucket, key, path):
            self.assertEqual((bucket, key), ("test-bucket", "models/spam-v1.json"))
            Path(path).write_text(json.dumps(original), encoding="utf-8")
        client = MagicMock()
        client.download_file.side_effect = download
        with patch.dict(os.environ, {"MODEL_BUCKET": "test-bucket", "MODEL_KEY": "models/spam-v1.json"}), patch.object(app.boto3, "client", return_value=client):
            self.assertEqual(app.initialize_model()["model_version"], "spam-v1")
            client.download_file.assert_called_once()

if __name__ == "__main__":
    unittest.main()
