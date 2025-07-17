import numpy as np
import pandas as pd
from sklearn.preprocessing import PowerTransformer
from sklearn.compose import TransformedTargetRegressor
from sklearn.ensemble import RandomForestRegressor,StackingRegressor
from lightgbm import LGBMRegressor
from sklearn.linear_model import LinearRegression
from pathlib import Path

import logging
import pickle
import os
import yaml
import mlflow

#configure logging
logger=logging.getLogger('model_building')
logger.setLevel(logging.DEBUG)

#configure console handler
file_handler=logging.StreamHandler()
file_handler.setLevel(logging.DEBUG)

#add handler to logger
logger.addHandler(file_handler)

#configure formatter
formatter=logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

def load_data(file_path):
    """
    Load a single pickle file.

   
    """
    try:
        logger.info(f"Loading data from: {file_path}")
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        logger.info(f"Loaded data successfully from: {file_path}")
        return data
    except Exception as e:
        logger.error(f"Error loading pickle file at {file_path}: {e}")
        raise

def load_params(params_path: str):
    """
    Load parameters from a pickle file.
    """
    try:
        logger.info(f"Loading parameters from: {params_path}")
        with open(params_path, 'rb') as f:
            params = yaml.safe_load(f)
        logger.info("Parameters loaded successfully.")
        return params

    except FileNotFoundError as e:
        logger.error(f"Parameter file not found at {params_path}: {e}")
        raise

def train_model(model, x_train, y_train):
    """
    Train the model using the provided training data.

    """
    logger.info("Starting model training...")
    model.fit(x_train, y_train)
    logger.info("Model training completed.")
    return model

def save_model(model, save_path):
    """
    Save the trained model to a file using pickle.
    """
    try:
        logger.info(f"Saving model to {save_path}...")
        with open(save_path, 'wb') as f:
            pickle.dump(model, f)  # ✅ Pass the model
        logger.info("Model saved successfully.")
    except Exception as e:
        logger.error(f"Failed to save model: {e}")
        raise

def save_transformer(transformer, save_path):
    """
    Save the fitted transformer to a file using pickle.
    """
    try:
        logger.info(f"Saving transformer to {save_path}...")
        with open(save_path, 'wb') as f:
            pickle.dump(transformer, f)  # ✅ Pass the transformer
        logger.info("Transformer saved successfully.")
    except Exception as e:
        logger.error(f"Failed to save transformer: {e}")
        raise

def main():

    current_dir=Path(__file__).resolve()
    print(current_dir)
    #get the root directory
    root_dir=current_dir.parent.parent.parent

    #load params from root directory
    params_path=root_dir/'params.yaml'
    params=load_params(params_path)
    rf_params=params['model_building']['rf_params']
    lgbm_params=params['model_building']['lgbm_params']

    
    x_train_path = root_dir / "data" / "processed" / "x_train_trans.pkl"
    y_train_path = root_dir / "data" / "processed" / "y_train.pkl"

    x_train = load_data(x_train_path)
    y_train = load_data(y_train_path)


    rf_regressor=RandomForestRegressor(**rf_params)
    lgbm_reg=LGBMRegressor(**lgbm_params)

    transformer=PowerTransformer()
    #meta model
    lr=LinearRegression()

    stacking_reg=StackingRegressor(estimators=[('rf',rf_regressor),('lgbm_reg',lgbm_reg)],final_estimator=lr)

    model=TransformedTargetRegressor(regressor=stacking_reg,transformer=transformer)
    model.fit(x_train,y_train)

    save_model(model, Path(root_dir / 'model.pkl'))
    save_transformer(transformer,Path(root_dir/'transformer.pkl'))

if __name__ == "__main__":
    main()
