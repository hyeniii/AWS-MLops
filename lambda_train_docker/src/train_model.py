"""
This module provides functions for training a Random Forest Classifier, saving the train and 
test data and saving a pickled trained model. 
"""
import logging
import typing
import sys
import pickle
from pathlib import Path
from joblib import dump

import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import OneHotEncoder

# Set logger
logger = logging.getLogger(__name__)

def train_model(train: pd.DataFrame, test:pd.DataFrame, target_var: str, initial_features: typing.List[str],
                rf_params: dict, k_cv: int = 5) -> typing.Tuple[
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
        k_cv: number of corss-validation folds. Defaults to 5.

    Returns:
        Tuple: A tuple containing:
            - The best trained random forest classifier from cross-validation.
            - A pandas DataFrame containing the training data used to train the model.
            - A pandas DataFrame containing the test data used to evaluate the trained model.
            - A pandas DataFrame containing the cross-validation results.
    """
    # --- Bind the two datasets to then do OHE on categoricals ---

    # Add dummy to identify entries in each dataset.
    train["train"] = 1
    test["train"] = 0
    logger.debug("train identifier added to train and test dataframes.")
    
    #  Check if train and test have the same columns 
    if set(train.columns) != set(test.columns):
        logger.error("Error. Train and test dataframe columns differ. Can't continue with training.")
        sys.exit(1)

    # Concat the two dataframes
    data = pd.concat([train, test], ignore_index=True)
    logger.info("Train and test dataframes binded together.")

    # --- Split data into features & target ---
    logger.info("Splitting data in train and test...")    
    target = data[[target_var,"train"]]
    initial_features.append("train")
    features = data[initial_features]
    logger.debug("Features and target extracted.")
    
    # --- OHE Categorical Features ---
    # Identify categorical variables
    logger.info("Identifying categorical features...")
    cat_features = features.select_dtypes(include=['object', 'category']).columns.tolist()
    logger.info("Categorical features identified: %s", cat_features)

    # OneHot Encoding for Selected Categorical Variables
    if cat_features:
        logger.info("OHE categorical features...")
        encoder = OneHotEncoder(sparse=False, handle_unknown='ignore')
        encoded_cats = encoder.fit_transform(features[cat_features])


        # Drop original categorical columns and concatenate encoded ones
        logger.info("Replacing categorical variables with OHE version.")
        features = features.drop(cat_features, axis=1)
        encoded_cats_df = pd.DataFrame(encoded_cats, columns=encoder.get_feature_names_out(cat_features))
        features = pd.concat([features, encoded_cats_df], axis=1)
        logger.info("Finished OHE of categorical features.")
  
    # --- Split data into train & test ---
    logger.info("Starting splitting of train and test...")

	# Split into train & test
    try:
        #x_train, x_test, y_train, y_test = train_test_split(features, target, 
        #                                                    test_size = test_size,
        #                                                    random_state = seed)
        x_train = features[features["train"] == 1].drop("train", axis = 1)
        x_test = features[features["train"] == 0].drop("train", axis = 1)
        y_train = target[target["train"] == 1].drop("train", axis = 1)
        y_test = target[target["train"] == 0].drop("train", axis = 1)
    except ValueError as err:
        logger.error("ValueError while splitting data intro train & test. The process can't "+
                     "continue. Error: ", err)
        sys.exit(1)
    except Exception as err:
        logger.error("Unexpected error while splitting data intro train & test. The process " +
                     "can't continue. Error: ", err)
        sys.exit(1)
    else:
        logger.info("Splitted features and target into train and test again.")
        logger.debug("Train features shape: %s", x_train.shape)
        logger.debug("Test features shape: %s", x_test.shape)

	
    # --- CV and hyperparameter tuning ---

    # Define a Random Forest object & grid search 
    logger.info("Starting modeling with cv for train data...")
    mod = RandomForestRegressor()
    grid_search = GridSearchCV(mod, param_grid = rf_params, cv = k_cv, n_jobs = -1, verbose = 1)

    # Fit model 
    try: 
        logger.info("Starting grid search fit:")
        #grid_search.fit(x_train[initial_features], y_train)
        grid_search.fit(x_train, y_train)
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
    return encoded_cats, best_model, train, test, cv_results


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

def save_encoder(encoder, filepath):
    """
    Save the One-Hot Encoder object to a file using joblib.

    Args:
        encoder: The One-Hot Encoder object to be saved.
        filepath: The file path where the encoder should be saved.
    """
    try:
        dump(encoder, filepath)
        logger.info("Encoder saved successfully to %s", filepath)
    except Exception as err:
        logger.warning("Error saving encoder. Process will continue without saving the encoder. Error: %s", eRR)