import boto3

sm_client = boto3.client("sagemaker", region_name="ap-south-1")

# First, delete the endpoint (if it exists)
try:
    sm_client.delete_endpoint(EndpointName="swiggy-time-predictor-endpoint")
    print("Deleted existing endpoint.")
except sm_client.exceptions.ClientError:
    print("No existing endpoint found.")

# Then, delete the endpoint config
try:
    sm_client.delete_endpoint_config(EndpointConfigName="swiggy-time-predictor-endpoint")
    print("Deleted existing endpoint config.")
except sm_client.exceptions.ClientError:
    print("No existing endpoint config found.")