"""Update an existing container-image Lambda, preserving its other settings."""
import argparse
import boto3
p = argparse.ArgumentParser()
p.add_argument("--image-uri", required=True)
p.add_argument("--function", default="group7-sentiment")
p.add_argument("--region", default="ap-southeast-1")
a = p.parse_args()
client = boto3.client("lambda", region_name=a.region)
client.update_function_code(FunctionName=a.function, ImageUri=a.image_uri)
client.get_waiter("function_updated").wait(FunctionName=a.function)
cfg = client.get_function_configuration(FunctionName=a.function)
print(cfg["FunctionName"], cfg["LastUpdateStatus"])
