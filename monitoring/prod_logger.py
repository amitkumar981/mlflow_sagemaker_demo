# monitoring/prod_logger.py

from pathlib import Path
import pandas as pd
from datetime import datetime

PROD_LOG_PATH = Path(__file__).resolve().parent / "production_data.csv"
PROD_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

def log_prediction_input(data: pd.DataFrame, prediction: float):
    row = data.copy()
    row["prediction"] = prediction
    row["timestamp"] = datetime.utcnow()

    # Append to existing file or create new one
    if PROD_LOG_PATH.exists():
        existing_data = pd.read_csv(PROD_LOG_PATH)
        updated_data = pd.concat([existing_data, row], ignore_index=True)
    else:
        updated_data = row

    # Trim to last 20 records
    trimmed_data = updated_data.tail(20)
    trimmed_data.to_csv(PROD_LOG_PATH, index=False)
