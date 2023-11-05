"""
This module provides functions for evaluating the regression model on the test set. 
Evaluation metrics are saved to a yaml file. 
"""
import logging
from pathlib import Path

import pandas as pd
from sklearn import metrics

import yaml

# Set logger
logger = logging.getLogger(__name__)

# Disable s3transfer debug logs
#logging.getLogger("s3transfer").setLevel(logging.WARNING)

def evaluate_performance(scores: pd.DataFrame) -> dict:
    """
    Evaluates model performance calculating AUC, accuracy, confusion metrics and the 
    classification report
     
    Args:
        scores: A pandas DataFrame with target, predicted probability and predicted class 
                for test set
        print_eval: A boolean indicating whether or not to print evaluation metrics. Defaults
                to False. 
    
    Returns:
        A dictionary containing the evaluation metrics (MAE, MSE, RMSE, R2)
    """
    eval_metrics = {}

    # --- Get evaluation metrics ---
    try:
        # MAE
        print("Calculating MAE")
        mae = metrics.mean_absolute_error(scores["y_test"], scores["y_pred"])
    except (ValueError, KeyError, IndexError) as err:
        print("An error occured when calculating MAE metric. The process will continue " +
                       "without MAE. Error: %s", err)
    else:
        eval_metrics["MAE"] = mae
        print("MAE metric calculated. MAE = %0.4f", mae)

    try:
        # MSE
        print("Calculating MSE")
        mse = metrics.mean_squared_error(scores["y_test"], scores["y_pred"])
    except (ValueError, KeyError, IndexError) as err:
        print("An error occured when calculating MSE metric. The process will " +
                       "continue without MSE. Error: %s", err)
    else:
        eval_metrics["MSE"] = mse
        print("MSE metric calculated. MSE = %0.4f", mse)

    try:
        # RMSE
        print("Calculating RMSE")
        rmse = metrics.mean_squared_error(scores["y_test"], scores["y_pred"], squared=False)
    except (ValueError, KeyError, IndexError) as err:
        print("An error occured when calculating RMSE metric. The process will " +
                       "continue without RMSE. Error: %s", err)
    else:
        eval_metrics["RMSE"] = rmse
        print("RMSE metric calculated. RMSE = %0.4f", rmse)

    try:
        # R2
        print("Calculating r2")
        r2 = metrics.r2_score(scores["y_test"], scores["y_pred"])
    except (ValueError, KeyError, IndexError) as err:
        print("An error occured when calculating R2 metric. The process will  " +
                       "continue without R2. Error: %f", err)
    else:
        eval_metrics["R2"] = r2
        print("R2 metric calculated. R2 = %f", r2)

    print("Evaluation metrics calculated. Evaluated metrics that were successfull: %s", eval_metrics)

    # Function output
    return eval_metrics


def save_metrics(metrics_dict: dict, save_path: Path) -> None:
    """
    Save evaluation metrics to a YAML file. 

    Args:
        metrics_dict: A dictionary containing the evaluation metrics (AUC, confMatrix, Accuracy, 
                      classifReport)
        save_path: The local path to the file where to save metrics to 
    """

    # Save metrics into yaml file
    try:
        print("Creating yaml file for metrics dictionary.")
        with open(save_path, "w", encoding="utf-8") as file:
            yaml.dump(metrics_dict, file)
    except yaml.YAMLError as err:
        print("Failed to save metrics to YAML file %s. The process will continue " +
                       "without saving evaluation metrics. Error: %s", save_path, err)
    except Exception as err:
        print("An unexpected error occurred when saving metrics to %s. The process will " +
                       "continue without saving evaluation metrics. Error: %s", save_path, err)
    else:
        print("Evaluation metrics dictionary successfully saved to %s", save_path)
