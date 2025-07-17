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
import pickle

# Add project root to sys.path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.append(str(project_root))
from monitoring.prod_logger import log_prediction_input


# Set up module paths
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from data_cleaning.data_cleaning_utils_py import perform_data_cleaning


# Set pandas output config
set_config(transform_output='pandas')

# Model + path loading
def load_model_information(file_path):
    with open(file_path) as f:
        return json.load(f)

current_dir = Path(__file__).resolve()
root_dir = current_dir.parent
model_path = project_root/'model.pkl'
preprocessor_path=project_root/'preprocessor.pkl'

with open(model_path,'rb') as f:
    model=pickle.load(f)

with open(preprocessor_path,'rb') as f:
    preprocessor=pickle.load(f)


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
    transformed_data=preprocessor.transform(cleaned_data)

    if cleaned_data.empty:
        return {"error": "No valid data after cleaning"}
    

    prediction = model.predict(transformed_data)[0]

    # Log the input and prediction
    log_prediction_input(pred_data, prediction)

    return {"prediction": float(prediction)}

# Optional custom route (can be used locally)
@app.post("/predict")
def do_predictions(data: Data):
    return invoke(data)

# Run locally
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)