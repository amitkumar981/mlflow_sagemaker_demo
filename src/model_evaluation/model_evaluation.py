import numpy as np
import pandas as pd
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.preprocessing import PowerTransformer
from sklearn.pipeline import Pipeline
from pathlib import Path
import pickle
import yaml
import json
import mlflow
from mlflow.models.signature import infer_signature
import logging
import os
from dotenv import  load_dotenv

# Configure logging
logger = logging.getLogger('model_evaluation')
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

dotenv_path = Path(__file__).resolve().parent.parent.parent / '.env'  # Adjust as needed
load_dotenv(dotenv_path,override=True)

tracking_uri = os.getenv('MLFLOW_TRACKING_URI')
logger.info(f"Loaded MLFLOW_TRACKING_URI = {tracking_uri}")
if not tracking_uri:
    raise ValueError("MLFLOW_TRACKING_URI is not set. Please check your .env file.")
mlflow.set_tracking_uri(tracking_uri)

class CustomModel(mlflow.pyfunc.PythonModel):
            def __init__(self,model,preprocessor):
                 self.model=model
                 self.preprocessor=preprocessor
            
            def predict(self, context, model_input):
                transformed_input = self.preprocessor.transform(model_input)
                return self.model.predict(transformed_input)
def load_pickle(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

def load_yaml(path):
    with open(path, 'rb') as f:
        return yaml.safe_load(f)

def save_model_info(path, model_name, run_id, artifact_path):
    info = {
        'model_name': model_name,
        'run_id': run_id,
        'artifact_path': artifact_path
    }
    with open(path, 'w') as f:
        json.dump(info, f, indent=4)
    logger.info(f"Model info saved at: {path}")

def main():
    
    mlflow.set_experiment("log_artifacts")
    with mlflow.start_run() as run:
        current_dir = Path(__file__).resolve()
        root_dir = current_dir.parent.parent.parent

        model_path = os.path.join(root_dir,"model.pkl")
        preprocessor_path = os.path.join(root_dir,"preprocessor.pkl")
        train_data_path = root_dir / 'data' / 'interim' / 'train_data.csv'
        test_data_path = root_dir / 'data' / 'interim' / 'test_data.csv'
        params_path = root_dir / 'params.yaml'

        # Load all files
        model = load_pickle(model_path)
        preprocessor = load_pickle(preprocessor_path)
        params = load_yaml(params_path)
        
        for key, value in params.items():
                logger.info(f'Logging parameter: {key} = {value}')
                mlflow.log_param(key, value)
                logger.info('All parameters logged successfully.')

        train_df = pd.read_csv(train_data_path).dropna()
        test_df = pd.read_csv(test_data_path).dropna()

        # Separate features and target
        x_train = train_df.drop(columns=["time_taken"])
        y_train = train_df["time_taken"]
        x_test = test_df.drop(columns=["time_taken"])
        y_test = test_df["time_taken"]

        x_train_trans = preprocessor.transform(x_train)
        x_test_trans = preprocessor.transform(x_test)

        y_train_pred = model.predict(x_train_trans)
        y_test_pred = model.predict(x_test_trans)

        # Log metrics
        mlflow.log_metric("train_mae", mean_absolute_error(y_train, y_train_pred))
        mlflow.log_metric("test_mae", mean_absolute_error(y_test, y_test_pred))
        mlflow.log_metric("train_r2", r2_score(y_train, y_train_pred))
        mlflow.log_metric("test_r2", r2_score(y_test, y_test_pred))
        logger.info(f"log all metrices successfully")

       #change data into mlflow dataframe
        train_data_input=mlflow.data.from_pandas(train_df.head(20),targets='time_taken')
        test_data_input=mlflow.data.from_pandas(test_df.head(20),targets='time_taken')

            #saving data into mlflow
        mlflow.log_input(dataset=train_data_input,context='training')
        mlflow.log_input(dataset=test_data_input,context='validation')
        logger.info(f"log datasets successfully")

        sample_input = x_train.sample(20, random_state=42)
        transformed_input=preprocessor.transform(sample_input)
        signature = mlflow.models.infer_signature(model_input=sample_input,
                                                    model_output=model.predict(transformed_input))
        
        
        mlflow.pyfunc.log_model(
        artifact_path="swiggy_time_predictor",  
        python_model=CustomModel(model,preprocessor),                      
        registered_model_name="SwiggyTimePredictorModel",
        signature=signature 
        )

        logger.info("Model logged to MLflow.")

        # Save model info
        save_model_info(
            path=root_dir / "model_info.json",
            model_name="swiggy_time_predictor",
            run_id=run.info.run_id,
            artifact_path=mlflow.get_artifact_uri()
        )
        logger.info("Model_info logged to MLflow.")

if __name__ == "__main__":
    main()




    


      
    
    
 