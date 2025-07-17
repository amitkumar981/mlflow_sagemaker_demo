import os
import boto3
import sagemaker
from sagemaker.model import Model
from dotenv import load_dotenv
from pathlib import Path

def main():
    # Load environment variables from .env
    dotenv_path = Path(__file__).resolve().parent / '.env'
    load_dotenv(dotenv_path, override=True)

    region = os.getenv('AWS_DEFAULT_REGION', 'ap-south-1')
    role = os.getenv('SAGEMAKER_ROLE','arn:aws:iam::565393027942:role/sagemaker_execution_role')
    account_id = boto3.client('sts').get_caller_identity()['Account']
    
    repo_name = "swiggytimepredictor"
    image_uri = f"{account_id}.dkr.ecr.{region}.amazonaws.com/{repo_name}:latest"

    print(f"🚀 Deploying image: {image_uri}")

    # Initialize SageMaker session
    session = sagemaker.Session()

    model = Model(
        image_uri=image_uri,
        role=role,
        name="swiggy-time-predictor-docker",
        sagemaker_session=session,
        env={
            "MLFLOW_TRACKING_URI": os.getenv("MLFLOW_TRACKING_URI", "")
        }
    )

    # Deploy model
    endpoint_name = "swiggy-time-predictor-endpoint"
    model.deploy(
        initial_instance_count=1,
        instance_type="ml.t2.medium",
        endpoint_name=endpoint_name
    )

    print(f"✅ Endpoint deployed: {endpoint_name}")

if __name__ == "__main__":
    main()

