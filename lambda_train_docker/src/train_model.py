"""
This module provides functions for training a Random Forest Classifier, saving the train and 
test data and saving a pickled trained model. 
"""
import logging
import typing
import sys
import pickle
from pathlib import Path

import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split

# Set logger
logger = logging.getLogger(__name__)

def train_model(data: pd.DataFrame, target_var: str, initial_features: typing.List[str],
                rf_params: dict, test_size: float = 0.2, seed: int = 11318, k_cv: int = 5) -> typing.Tuple[
                    RandomForestRegressor, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Train a random forest classifier using the specified input features.

    Args:
        data: The pandas DataFrame containing the features to use for training the model.
        target_var: Name of the target variable.
        initial_features: The list of feature names to use for training the model.
        rf_params: dictionary with the parameters used for defining the model. The keys 
                   should include n_estim (number of trees) and depth (maximum depth of 
                   each tree).
        test_size: The proportion of the input data to use for testing the trained model.
                   Defaults to 0.2
        seed: integer to set seed for random splitting and cv. Defaults to 11318
        k_cv: number of corss-validation folds. Defaults to 5.

    Returns:
        Tuple: A tuple containing:
            - The best trained random forest classifier from cross-validation.
            - A pandas DataFrame containing the training data used to train the model.
            - A pandas DataFrame containing the test data used to evaluate the trained model.
            - A pandas DataFrame containing the cross-validation results.
    """
	# --- Split data into train & test ---
    logger.info("Splitting data in train and test.")
    target = data[target_var]
    features = data.drop(target_var, axis = 1)
    logger.debug("Features and target extracted.")
    
    # Validate test_size in (0,1)
    try:
        assert 0 <test_size < 1
    except AssertionError:
        logger.error("Invalid test_size. Received %f but test size should be in (0,1). Setting " +
                       "test_size to default value (0.2).", test_size)
        test_size = 0.2
    else:
        logger.error("    test size: %s", test_size)

	# Split into train & test
    try:
        x_train, x_test, y_train, y_test = train_test_split(features, target, 
                                                            test_size = test_size,
                                                            random_state = seed)
    except ValueError as err:
        logger.error("ValueError while splitting data intro train & test. The process can't "+
                     "continue. Error: ", err)
        sys.exit(1)
    except Exception as err:
        logger.error("Unexpected error while splitting data intro train & test. The process " +
                     "can't continue. Error: ", err)
        sys.exit(1)
    else:
        logger.info("Splitted features and target into train and test. Test size = %0.2f%%",
                    test_size*100)
        logger.debug("Train features shape: %s", x_train.shape)
        logger.debug("Test features shape: %s", x_test.shape)

	
    # --- CV and hyperparameter tuning ---
    
    # Define a Random Forest object & grid search 
    logger.info("Starting modeling with cv for train data.")
    mod = RandomForestRegressor()
    grid_search = GridSearchCV(mod, param_grid = rf_params, cv = k_cv, n_jobs = -1, verbose = 1)

    # Fit model 
    try: 
        logger.info("Starting grid search fit:")
        grid_search.fit(x_train[initial_features], y_train)
    except Exception as err:
        logger.error("Unexpected error occured during cross-validation. The process can't continue. " +
              "Error: %s", err)
        sys.exit(1)
    else:
        logger.info("Cross-validation completed. Best parameters found: %s ", grid_search.best_params_)
        
        # Get best model & cv results
        best_model = grid_search.best_estimator_
        cv_results = pd.DataFrame(grid_search.cv_results_)
        logger.info("Best model and cv results extracted.")

    # Bind x_train and y_train
    train = x_train.copy()
    train = train.assign(**{target_var: y_train})
    logger.debug("Train data extracted.")

	# Bind x_test and y_test
    test = x_test.copy()
    test = test.assign(**{target_var: y_test})
    logger.debug("Test data extracted.")

	# Function output
    logger.info("Modeling done. Returning best model, train set, test set and cv results.")
    return best_model, train, test, cv_results


def save_data(train: pd.DataFrame, test: pd.DataFrame, cv_results: pd.DataFrame, save_dir: Path) -> None:
    """
    Save train and test data as CSV files to a specified directory.

    Args:
        train: Pandas DataFrame containing the training data.
        test: Pandas DataFrame containing the test data.
        cv_results: Pandas DataFrame containing the cv results.
        save_dir: Local directory where train and test data will be saved.
    """
    # Save train
    try:
        train_file = save_dir / "train.csv"
        logger.info("Saving training data to %s", train_file)
        train.to_csv(train_file, index = False)
    except FileNotFoundError:
        logger.warning("File %s not found. The process will continue without saving the train " +
                       "data to csv. Please provide a valid directory to save train data to.", 
                       train_file)
    except PermissionError:
        logger.warning("The process does not have the necessary permissions to create or write " +
                       "to the file %s. The process will continue without saving the train data.",
                        train_file)
    except Exception as err:
        logger.warning("An unexpected error occurred when saving train data to file %s. The " +
                       "process will continue without saving the train data. Error: %s", train_file,
                        err)
    else:
        logger.info("Train data saved to file %s", train_file)

	# Save test
    try:
        test_file = save_dir / "test.csv"
        logger.info("Saving test data to %s", test_file)
        test.to_csv(test_file, index = False)
    except FileNotFoundError:
        logger.warning("File %s not found. The process will continue without saving the test " +
                       "data to csv. Please provide a valid directory to save test data to.", 
                       test_file)
    except PermissionError:
        logger.warning("The process does not have the necessary permissions to create or write " +
                       "to the file %s. The process will continue without saving the test data.",
                       test_file)
    except Exception as err:
        logger.warning("An unexpected error occurred when saving test data to %s. The process " +
                       "will continue without saving the test data. Error: %s", test_file, err)
    else:
        logger.info("Test data saved to file %s", test_file)

    # Save cv results
    try:
        cv_file = save_dir / "cv_results.csv"
        logger.info("Saving cv results to %s", train_file)
        cv_results.to_csv(cv_file, index = False)
    except FileNotFoundError:
        logger.warning("File %s not found. The process will continue without saving the cv " +
                       "results to csv. Please provide a valid directory to save cv results to.", 
                       cv_file)
    except PermissionError:
        logger.warning("The process does not have the necessary permissions to create or write " +
                       "to the file %s. The process will continue without saving the cv results.",
                       cv_file)
    except Exception as err:
        logger.warning("An unexpected error occurred when saving cv results to %s. The process " +
                       "will continue without saving the cv results. Error: %s", cv_file, err)
    else:
        logger.info("CV results saved to file %s", cv_file)


def save_model(tmo: RandomForestRegressor, save_path: Path) -> None:
    """
    Saves a trained random forest model to a pickle file at the specified location.

    Args:
        tmo (RandomForestRegressor): The trained random forest model to be saved.
        save_path (Path): The path where the model will be saved.
    """
    try:
        # Save pickle file
        logger.info("Saving pickle file with tmo to %s", save_path)
        with open(save_path, "wb") as file:
            pickle.dump(tmo, file)
    except pickle.PicklingError:
        logger.warning("Unable to pickle the model. The process will continue without saving " +
                       "the model.")
    except FileNotFoundError:
        logger.warning("File %s not found. The process will continue without saving the model. " +
                       "Please provide a valid directory to save the pickled model to.", save_path)
    except PermissionError:
        logger.warning("The process does not have the necessary permissions to create or write " +
                       "to the file %s. The process will continue without saving the pickled " +
                       "model.", save_path)
    except Exception as err:
        logger.warning("An error occurred while saving the pickled model. The process will " +
                       "continue without saving the pickled model. Error: %s", err)
    else:
        logger.info("Model saved as pickle file at %s", save_path)
