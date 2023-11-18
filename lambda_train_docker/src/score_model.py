"""
This module provides functions for scoring the trained regression model and saving scores to a csv file.
"""
import logging
import sys
import typing
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestRegressor

# Set logger
logger = logging.getLogger(__name__)

def score_model(test_df: pd.DataFrame, tmo: RandomForestRegressor, target_var: str) -> pd.DataFrame:
    """
    Predict target for test set using a trained Random Forest model.

    Args:
        test_df: A Pandas DataFrame containing the test features and target.
        target_var: Name of the target variable. 
        tmo: A trained Random Forest model.
        initial_features: A list of strings representing the features to be selected for
                          scoring the model.

    Returns:
        scores: A Pandas DataFrame with two columns, 'y_test', 'ypred',
                representing the target, and its prediciton, respectively
    """

    # Get test features
    x_test  = test_df.drop(target_var, axis = 1)
    y_test = test_df[target_var]
    logger.info("Test features and target extracted.")
    logger.debug("Test set shape: %s", x_test.shape)

    # --- Predictions ---
    logger.info("Predicting values for test set")
    try:
        # Predict target for test set
        y_pred = tmo.predict(x_test)
    except (KeyError, TypeError) as err:
        logger.error("An error occurred when predicting values for the test set. " +
                    "The process can't continue. Error: %s", err)
        sys.exit(1)
    except Exception as err:
        logger.error("An unexpected error occurred when predicting values for the test " +
                    "set. The process can't continue. Error: %s", err)
        sys.exit(1)
    else:
        logger.info("Predicted values for test set completed.")

    # Define scores as pandas dataframe
    scores = pd.DataFrame({"y_test":y_test,
                           "y_pred":y_pred})
    logger.info("Scores dataframe succesfully created.")
    logger.debug("Socres dataframe shape: %s", scores.shape)

    # Function output
    return scores


def save_scores(scores: pd.DataFrame, save_path: Path) -> None:
    """
    Save test scores to a CSV file.

    Args:
        scores (pd.DataFrame): Pandas DataFrame with test scores.
        save_path (Path): Path to file where scores will be saved.
    """
    try:
        logger.info("Saving scores to file %s", save_path)
        scores.to_csv(save_path, index = False)
    except FileNotFoundError:
        logger.warning("File %s not found. The process will continue without saving the scores " +
                       "to csv. Please provide a valid directory to save scores to.", save_path)
    except PermissionError:
        logger.warning("The process does not have the necessary permissions to create or write " +
                       "to the file %s. The process will continue without saving the scores.",
                        save_path)
    except Exception as err:
        logger.warning("An unexpected error occurred when saving scores to file %s. The process " +
                       "will continue without saving the scores. Error: %s", save_path, err)
    else:
        logger.info("Scores dataframed saved to file %s", save_path)
