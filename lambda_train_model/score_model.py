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

def score_model(test_df: pd.DataFrame, tmo: RandomForestRegressor, target_var: str, 
                initial_features: typing.List[str]) -> pd.DataFrame:
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
    print("Test set shape: %s", x_test.shape)

    # --- Predictions ---
    try:
        # Predict target for test set
        print("Predicting values for test set")
        y_pred = tmo.predict(x_test[initial_features])
    except (KeyError, TypeError) as err:
        print("An error occurred when predicting values for the test set. " +
                    "The process can't continue. Error: %s", err)
        sys.exit(1)
    except Exception as err:
        print("An unexpected error occurred when predicting values for the test " +
                    "set. The process can't continue. Error: %s", err)
        sys.exit(1)
    else:
        print("Predicted values for test set completed.")

    # Define scores as pandas dataframe
    scores = pd.DataFrame({"y_test":y_test,
                           "y_pred":y_pred})
    print("Scores dataframe succesfully created.")
    print("Socres dataframe shape: %s", scores.shape)

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
        print("Saving scores to file %s", save_path)
        scores.to_csv(save_path, index = False)
    except FileNotFoundError:
        print("File %s not found. The process will continue without saving the scores " +
                       "to csv. Please provide a valid directory to save scores to.", save_path)
    except PermissionError:
        print("The process does not have the necessary permissions to create or write " +
                       "to the file %s. The process will continue without saving the scores.",
                        save_path)
    except Exception as err:
        print("An unexpected error occurred when saving scores to file %s. The process " +
                       "will continue without saving the scores. Error: %s", save_path, err)
    else:
        print("Scores dataframed saved to file %s", save_path)
