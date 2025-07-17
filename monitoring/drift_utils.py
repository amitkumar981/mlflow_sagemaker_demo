import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset

def generate_drift_report(reference: pd.DataFrame, current: pd.DataFrame):
    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=reference, current_data=current)
    return report
