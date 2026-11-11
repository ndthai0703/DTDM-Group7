import json
import unittest

from unittest.mock import patch
import lambda_function as app


class LambdaTests(unittest.TestCase):
    def invoke(self, text):
        result = app.lambda_handler(
            {
                "httpMethod": "POST",
                "body": json.dumps({"text": text}),
            },
            None
        )

        return (
            result["statusCode"],
            json.loads(result["body"])
        )

    def test_positive(self):
        status, body = self.invoke(
            "excellent product good quality"
        )

        self.assertEqual(status, 200)
        self.assertEqual(body["label"], "positive")
        self.assertTrue(
            0.5 <= body["confidence"] <= 1
        )
        self.assertGreaterEqual(
            body["processing_ms"], 0
        )

    def test_negative(self):
        status, body = self.invoke(
            "terrible product bad quality"
        )

        self.assertEqual(status, 200)
        self.assertEqual(body["label"], "negative")

    def test_invalid_input(self):
        for text in ("", " ", 123, "a" * 2001):
            self.assertEqual(
                self.invoke(text)[0], 400
            )

    def test_invalid_json(self):
        result = app.lambda_handler(
            {"body": "{"},
            None
        )

        self.assertEqual(
            result["statusCode"], 400
        )

    def test_unknown_words(self):
        self.assertEqual(
            self.invoke("zzzxxy qqqwww")[0],
            422
        )

    def test_reuse_model(self):
        with patch.object(app, "load_model") as loader:
            self.invoke("excellent product")
            self.invoke("terrible product")

            loader.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)