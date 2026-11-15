"""Explicit smoke test of a deployed endpoint. Writes two history records."""
import argparse
import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Full HTTPS /predict endpoint, including stage")
    args = parser.parse_args()
    if not args.url.startswith("https://"):
        parser.error("Use HTTPS")
    for text, expected in [("Congratulations! You won free cash! Claim your prize now.", "spam"),
                           ("Please send me the report before tomorrow.", "ham"), ("", None)]:
        req = Request(args.url, data=json.dumps({"text": text}).encode(), headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urlopen(req, timeout=35) as res:
                status, data = res.status, json.load(res)
        except HTTPError as err:
            status, data = err.code, json.loads(err.read())
        if expected:
            if status != 200 or data.get("label") != expected or data.get("history_saved") is not True:
                raise RuntimeError(f"Unexpected response: {status} {data}")
        elif status != 400:
            raise RuntimeError(f"Expected 400: {status} {data}")
        print(status, json.dumps(data))
if __name__ == "__main__":
    main()
