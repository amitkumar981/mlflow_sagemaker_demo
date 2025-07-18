import pytest
import mlflow
from mlflow import MlflowClient
import os
import json
import logging
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI'))

def model_load_information(file_path):
    with open(file_path,'rb') as f:
        run_info=json.load(f)
    return run_info

current_dir=Path(__file__).resolve()
root_path=current_dir.parent.parent
print('root_path',root_path)

file_path = root_path/'model_info.json'
model_name=model_load_information(file_path=file_path)['model_name']


@pytest.mark.parametrize(
    ("model_name", "stage"),
    [(model_name, None)]  # You can replace None with "Staging" if needed
)
def test_load_model_from_registry(model_name, stage):
    client = MlflowClient()

    if stage:
        latest_versions = client.get_latest_versions(name=model_name, stages=[stage])
    else:
        latest_versions = client.get_latest_versions(name=model_name)

    assert latest_versions, f"No model versions found for '{model_name}'"

    latest_version = latest_versions[0].version
    model_path = f"models:/{model_name}/{stage}" if stage else f"models:/{model_name}/{latest_version}"

    model = mlflow.pyfunc.load_model(model_path)
    assert model is not None, "Failed to load model from registry"

    print(f"Model '{model_name}' version {latest_version} loaded successfully from stage: {stage or 'None'}")

