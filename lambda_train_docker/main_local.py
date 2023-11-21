# responsible for orchestration

import argparse
import datetime
import logging.config
from pathlib import Path
import pandas as pd

import yaml

import evaluate_performance as ep
import score_model as sm
import train_model as tm

# set up logger config for some file 
logging.config.fileConfig("../../config/logging/local.conf")
logger = logging.getLogger("clouds")

# Execute each step of the pipeline:
if __name__ == "__main__":
    
    # --- Set argparser instance to handle command line arguments ---
    # Project description 
    parser = argparse.ArgumentParser(
        description="Acquire, clean, and create features from clouds data"
    )
    # Add configuration file. 
    parser.add_argument(
        "--config", default="../../config/model-config.yaml", help="Path to configuration file"
    )
    # Parse command line arguments
    args = parser.parse_args()

    # Load configuration file for parameters and run config
    with open(args.config, "r") as f:
        try:
            config = yaml.load(f, Loader=yaml.FullLoader)
        except yaml.error.YAMLError as e:
            logger.error("Error while loading configuration from %s", args.config)
        else:
            logger.info("Configuration file loaded from %s", args.config)

    # Access run_config key from yaml config file. If it does not exist the
    # default is an empty dictionary. 
    run_config = config.get("run_config", {})
    
    # Set up output directory for saving artifacts, takes current timestamp as subfolder
    now = int(datetime.datetime.now().timestamp())
    artifacts = Path(run_config.get("output", "runs")) / str(now)
    artifacts.mkdir(parents=True)

    # Save config file to artifacts directory for traceability
    with (artifacts / "config.yaml").open("w") as f:
        yaml.dump(config, f)

    # Read toy data
    data = pd.read_csv(run_config["clean_data_key"])
    logging.info("Data loaded from file %s", run_config["clean_data_key"])

    # Split data into train/test set and train model based on config; save each to disk
    logging.info("Starting model training")
    # Split data into train/test set and train model based on config; save each to disk
    encoder, tmo, train, test, cv_result = tm.train_model(data,  **config["train_model"])
    logging.info("Finish model training.")
    tm.save_en(train, test, cv_result, artifacts)
    logging.info("Train, test, cv_results saved to folder %s.", artifacts)
    tm.save_data(train, test, cv_result, artifacts)
    logging.info("Train, test, cv_results saved to folder %s.", artifacts)
    tm.save_model(tmo, artifacts/"tmo.pkl")
    logging.info("Model saved to folder %s.", artifacts)
    tm.save_model(encoder, artifacts/"encoder.joblib")
    logging.info("Encoder for categorical variables saved to folder %s.", artifacts)

    # Score model on test set; save scores to disk
    logging.info("Starting model scring")
    scores = sm.score_model(test, tmo, **config["score_model"])
    logging.info("finished model scoring")
    sm.save_scores(scores, artifacts/"scores.csv")
    logging.info("Scoring saved to folder")

    # Evaluate model performance metrics; save metrics to disk
    logging.info("Starting evaluation of model.")
    metrics = ep.evaluate_performance(scores)
    logging.info("Model evaluation finished.")
    ep.save_metrics(metrics, artifacts/"metrics.yaml")
    logging.info("Model evaluation saved to folder")