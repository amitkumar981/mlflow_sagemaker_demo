import pytest
import mlflow
from mlflow.tracking import MlflowClient
import os
import json
from dotenv import load_dotenv
import pickle
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import PowerTransformer
from pathlib import Path


load_dotenv(override=True)
mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI'))
client = MlflowClient()

def model_load_information(file_path):
    with open(file_path, 'r') as f:
        run_info = json.load(f)
    return run_info

# Load run info
current_dir=Path(__file__)
root_path=current_dir.parent.parent
file_path = root_path/'model_info.json'
run_info = model_load_information(file_path)

model_name = run_info['model_name']

client=MlflowClient()
latest_versions = client.get_latest_versions(name=model_name)
latest_version=latest_versions[0].version

# Load model
model_path = f"models:/{model_name}/{latest_version}"
model = mlflow.pyfunc.load_model(model_path)

data_path=os.path.join(root_path,'data','interim','test_data.csv')

transformer=PowerTransformer()


@pytest.mark.parametrize(argnames="model, data_path, threshold_error",
                        argvalues=[(model,data_path,5)])

def test_model_performance(model,data_path,threshold_error):

    #load data set
    df=pd.read_csv(data_path)

    # drop missing values
    df.dropna(inplace=True)

    #split x and y
    x=df.drop(columns=['time_taken'])
    y=df['time_taken']

    #get predictions
    y_pred=model.predict(x)

    #calculate error
    mean_error=mean_absolute_error(y_pred,y)

       # check for performance
    assert mean_error <= threshold_error, f"The model does not pass the performance threshold of {threshold_error} minutes"
    print("The avg error is", mean_error)
    
    print(f"The {model_name} model passed the performance test")




















