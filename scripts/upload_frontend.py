"""Upload index.html only; does not change bucket public-access settings."""
import argparse
from pathlib import Path
import boto3
p = argparse.ArgumentParser()
p.add_argument("--bucket", required=True)
p.add_argument("--region", default="ap-southeast-1")
a = p.parse_args()
file = Path(__file__).resolve().parents[1] / "frontend/index.html"
if 'const API_URL = "";' in file.read_text(encoding="utf-8"):
    raise SystemExit("Set API_URL in frontend/index.html first")
boto3.client("s3", region_name=a.region).upload_file(str(file), a.bucket, "index.html",
    ExtraArgs={"ContentType": "text/html; charset=utf-8", "CacheControl": "no-cache"})
print("Uploaded index.html; use the website URL from the S3 console.")
