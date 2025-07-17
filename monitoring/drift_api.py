from fastapi import FastAPI
from pathlib import Path
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST, Counter
from prometheus_api_client import PrometheusConnect
from fastapi.responses import Response
from drift import calculate_drift_metrics

app = FastAPI()
prediction_count = Counter('prediction_count', 'Number of predictions made')

# Initialize Prometheus client
prom = PrometheusConnect(url="http://prometheus:9090", disable_ssl=True)

# Paths
root_dir = Path(__file__).resolve().parent.parent
reference_path = root_dir / 'data' / 'raw' / 'swiggy.csv'
current_path = root_dir / 'monitoring' / 'production_data.csv'

# Prometheus Gauges
drifted_columns_count_gauge = Gauge("drifted_columns_count", "Number of columns with drift")
drift_share_gauge = Gauge("drift_share", "Share of columns with drift")
column_drift_pvalue_gauge = Gauge("column_drift_pvalue", "P-value for drift in each column", ["column"])

def update_drift_metrics():
    result = calculate_drift_metrics(reference_path, current_path)

    drifted_columns_count_gauge.set(result["drifted_count"])
    drift_share_gauge.set(result["drift_share"])

    for column, pval in result["column_pvalues"].items():
        column_drift_pvalue_gauge.labels(column=column).set(pval)

@app.get("/drift")
def calculate_drift():
    update_drift_metrics()
    return {
        "drifted_columns": drifted_columns_count_gauge._value.get(),
        "drift_share": drift_share_gauge._value.get(),
        "column_pvalues": {
            label[0]: metric._value.get()
            for label, metric in column_drift_pvalue_gauge._metrics.items()
        }
    }

@app.get("/metrics")
def metrics():
    update_drift_metrics()  
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/ping")
def ping():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)






