import json
import boto3
client = boto3.client("lambda", region_name="ap-southeast-1")
print(json.dumps(client.get_account_settings(), default=str, indent=2))
