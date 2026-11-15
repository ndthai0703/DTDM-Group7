import argparse
from pathlib import Path
import boto3
p = argparse.ArgumentParser()
p.add_argument("--bucket", required=True)
p.add_argument("--key", default="models/spam-v1.json")
p.add_argument("--region", default="ap-southeast-1")
p.add_argument("--file", default=str(Path(__file__).resolve().parents[1] / "model/artifacts/spam-v1.json"))
a = p.parse_args()
boto3.client("s3", region_name=a.region).upload_file(a.file, a.bucket, a.key)
print(f"s3://{a.bucket}/{a.key}")
