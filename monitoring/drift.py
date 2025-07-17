# monitoring/drift_utils.py

import pandas as pd
from evidently import Dataset, DataDefinition, Report
from evidently.presets import DataDriftPreset
from pathlib import Path
import json

def calculate_drift_metrics(reference_path: Path, current_path: Path):
    reference_df = pd.read_csv(reference_path)
    current_df = pd.read_csv(current_path)

    for df in [reference_df, current_df]:
        if 'timestamp' in df.columns:
            df.drop(columns=['timestamp'], inplace=True)

    schema = DataDefinition(
        numerical_columns=[
            "Restaurant_latitude", "Restaurant_longitude",
            "Delivery_location_latitude", "Delivery_location_longitude",
            "Vehicle_condition"
        ],
        categorical_columns=[
            "Delivery_person_Age", "Delivery_person_Ratings", "Order_Date",
            "Time_Orderd", "Time_Order_picked", "Weatherconditions",
            "Road_traffic_density", "Type_of_order", "Type_of_vehicle",
            "multiple_deliveries", "Festival", "City"
        ],
    )

    eval_data_1 = Dataset.from_pandas(current_df, data_definition=schema)
    eval_data_2 = Dataset.from_pandas(reference_df, data_definition=schema)

    report = Report([DataDriftPreset()])
    result = report.run(eval_data_1, eval_data_2)

    result_dict = json.loads(result.json())

    drifted_count = 0
    drift_share = 0.0
    column_pvalues = {}

    for metric in result_dict.get("metrics", []):
        if "DriftedColumnsCount" in metric.get("metric_id", ""):
            drifted_count = metric["value"]["count"]
            drift_share = metric["value"]["share"]
        elif "ValueDrift" in metric.get("metric_id", ""):
            column = metric["metric_id"].split("column=")[-1].rstrip(")")
            column_pvalues[column] = metric["value"]

    return {
        "drifted_count": drifted_count,
        "drift_share": drift_share,
        "column_pvalues": column_pvalues
    }
