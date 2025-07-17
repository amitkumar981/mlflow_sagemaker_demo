from fastapi import FastAPI, Request
from pydantic import BaseModel
import numpy as np
import pandas as pd
import json
import joblib
from sklearn.pipeline import Pipeline
from sklearn import set_config
from pathlib import Path
import os
import sys
import mlflow
from mlflow import pyfunc
from dotenv import load_dotenv


# Set up module paths
sys.path.append(str(Path(__file__).resolve().parent / "src"))

from data_cleaning.data_cleaning_utils_py import perform_data_cleaning

# Load environment variables
dotenv_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path, override=True)

tracking_uri = os.getenv('MLFLOW_TRACKING_URI')
print(f"Loaded MLFLOW_TRACKING_URI = {tracking_uri}")
if not tracking_uri:
    raise ValueError("MLFLOW_TRACKING_URI is not set. Please check your .env file.")
mlflow.set_tracking_uri(tracking_uri)

# Set pandas output config
set_config(transform_output='pandas')

# Model + path loading
def load_model_information(file_path):
    with open(file_path) as f:
        return json.load(f)

current_dir = Path(__file__).resolve()
root_dir = current_dir.parent
info_path = root_dir / "model_info.json"
run_info = load_model_information(info_path)

model_name = 'swiggy_time_predictor'
run_id = run_info['run_id']
model_path = f"runs:/{run_id}/{model_name}"
model = mlflow.pyfunc.load_model(model_path)
print("✅ Model loaded.")

# FastAPI app
app = FastAPI()

# Health check
@app.get("/ping")
def ping():
    return {"status": "ok"}

# Inference input format
class Data(BaseModel):  
    ID: str
    Delivery_person_ID: str
    Delivery_person_Age: str
    Delivery_person_Ratings: str
    Restaurant_latitude: float
    Restaurant_longitude: float
    Delivery_location_latitude: float
    Delivery_location_longitude: float
    Order_Date: str
    Time_Orderd: str
    Time_Order_picked: str
    Weatherconditions: str
    Road_traffic_density: str
    Vehicle_condition: int
    Type_of_order: str
    Type_of_vehicle: str
    multiple_deliveries: str
    Festival: str
    City: str

# Required /invocations endpoint for SageMaker
@app.post("/invocations")
def invoke(data: Data):
    pred_data = pd.DataFrame([data.dict()])
    cleaned_data = perform_data_cleaning(pred_data).dropna()
    prediction = model.predict(cleaned_data)[0]
    return {"prediction": float(prediction)}

# Optional custom route (can be used locally)
@app.post("/predict")
def do_predictions(data: Data):
    return invoke(data)

# Run locally
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

   
    
