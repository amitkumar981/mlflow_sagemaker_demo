import logging
import mlflow
import json
from pathlib import Path
from mlflow import MlflowClient
import os
from dotenv import load_dotenv


load_dotenv(override=True)
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))


#configure logging
logger=logging.getLogger('register model')
logger.setLevel(logging.DEBUG)

#configure file handler
file_handler=logging.StreamHandler()
file_handler.setLevel(logging.DEBUG)

#add handler to logger
logger.addHandler(file_handler)

#cofigure fomatter
formatter=logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

def load_model_info(info_path:str):
    try:
        logger.info(f"loading model_info from :{info_path}")
        with open(info_path,'r') as f:
            model_info=json.load(f)
            logger.info(f"load model_info successfully from {info_path}")
            return model_info
    except Exception as e:
        logger.error(f"error in load model info as {e}")
        return None

def main():
    #get current dir
    current_dir=Path(__file__).resolve()
    print(current_dir)
    logger.info(f"current dir is {current_dir}")
    root_dir=current_dir.parent.parent.parent

    info_path=root_dir/'model_info.json'

    model_info=load_model_info(info_path)
     #get model name
    model_name=model_info['model_name']
    logger.info(f"get model name : {model_name} successfully")
    #get run_id
    run_id=model_info['run_id']
    logger.info(f"get run_id : {run_id} successfully")

    model_uri=f"runs:/{run_id}/{model_name}"

    #get model version
    model_version=mlflow.register_model(model_uri=model_uri,name=model_name)
    logger.info(f"get model version: {model_version} successfully")
    #get registered model version
    registered_model_version=model_version.version
    logger.info(f"get registered model version : {registered_model_version} successfully")
    #get registered model name
    registered_model_name=model_version.name
    logger.info(f"get registered model name : {registered_model_name} successfully")

    client=MlflowClient()
    #transistion model_stage
    client.transition_model_version_stage(
    name=registered_model_name,
    version=registered_model_version,
    stage='Staging'
    )
    logger.info(f"registered model successfully")

if __name__=="__main__":
    main()



    


        

        
   

