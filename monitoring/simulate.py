# simulate.py

import pandas as pd
import requests
import time
import random
import json
from pathlib import Path


current_dir=Path(__file__).resolve()
root_dir=current_dir.parent.parent
# Configuration
URL = "http://localhost:5000/invocations"
 
sample_data_path = root_dir/'data'/'raw'/'swiggy.csv'  

# Feature categories
traffic_order = ['medium', 'high', 'jam', 'low']
distance_order = ['short', 'medium', 'long', 'very long']

# Load and shuffle data
df = pd.read_csv(sample_data_path)
df = df.sample(frac=1).reset_index(drop=True)

def add_variability(row):
    try:
        # Clean and handle NaNs for numeric fields
        age = row['Delivery_person_Age']
        if pd.isna(age) or str(age).strip().lower() in ['nan', 'nan ', 'none', 'null', '']:
            row['Delivery_person_Age'] = "25"  # or some default
        else:
            row['Delivery_person_Age'] = str(int(float(age)) + random.choice([-1, 0, 1]))

        ratings = row['Delivery_person_Ratings']
        if pd.isna(ratings) or str(ratings).strip().lower() in ['nan', 'nan ', 'none', 'null', '']:
            row['Delivery_person_Ratings'] = "4.5"
        else:
            row['Delivery_person_Ratings'] = str(round(float(ratings) + random.uniform(-0.1, 0.1), 2))

        if 'Vehicle_condition' in row:
            try:
                row['Vehicle_condition'] = int(float(row['Vehicle_condition']))
            except:
                row['Vehicle_condition'] = 3  # default

        # Add more fields as needed...

    except Exception as e:
        print(f"⚠️ Error adjusting row: {e}")
    
    return row


# Simulate streaming
for i, row in df.iterrows():
    data = add_variability(row).to_dict()

    # Fix type mismatches
    if isinstance(data.get("Vehicle_condition"), float):
        data["Vehicle_condition"] = int(data["Vehicle_condition"])

    # Drop unwanted keys if they exist (e.g., target column or old transformations)
    data.pop("time_taken", None)
    data.pop("distance_type", None)

    try:
        response = requests.post(URL, json=data)
        print(f"[{i+1}] Sent → Status: {response.status_code} | Response: {response.json()}")
    except Exception as e:
        print(f"[{i+1}] ❌ Failed: {e}")

    time.sleep(random.uniform(1.5, 5))  # Simulate delay between API calls
