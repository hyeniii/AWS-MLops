import json
import boto3
import os

import logging
import yaml
import pandas as pd 
from pathlib import Path

import src.train_model as tm
import src.score_model as sm
import src.evaluate_performance as ep
import src.aws_utils as au

from configparser import ConfigParser

# Set logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
  try:
    logger.info("**STARTED**")
    
    #
    # setup AWS S3 access based on config file:
    #
    logger.info("Setting AWS S3 accesss...")
    config_file = './config/config.ini' 
    s3_profile = 'aws-mlops-s3readwrite' 
    
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
    boto3.setup_default_session(profile_name=s3_profile)
    
    configur = ConfigParser()
    logger.info("Reading AWS config file.")
    configur.read(config_file)
    bucketname = configur.get('s3', 'bucket_name')
    
    logger.info("Setting S3 client with boto3.")
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucketname)

    logger.info("Finish setting up AWS S3 access.")

    #
    # extract model config file key from event: could be a parameter
    # or could be part of URL path ("pathParameters"):
    #
    logger.info("Start extracting model config file.")
  
    if "modelConfigKey" in event:
      modelConfigKey = event["modelConfigKey"]
      logger.info("modelConfigKey in event: %s", modelConfigKey)
    elif "pathParameters" in event:
      if "modelConfigKey" in event["pathParameters"]:
        modelConfigKey = event["pathParameters"]["modelConfigKey"]
        logger.info("modelConfigKey in pathParams: %s", modelConfigKey)
      else:
        raise Exception("requires modelConfigKey parameter in pathParameters")
    else:
        raise Exception("requires modelConfigKey parameter in event")
        
    logger.info("Extracted modelConfigKey: %s", modelConfigKey)
    
    modelConfigKey = "config/" + modelConfigKey

    # ----------------------------------------------------------------
    # download model config file from S3 to local filesystem:
    # ----------------------------------------------------------------
    # Set local name for model config file
    modelConfig_filename = "/tmp/model-config.yaml"

    # Download file from s3
    logger.info("**Downloading model config file from S3**")
    bucket.download_file(modelConfigKey, modelConfig_filename)
    
    # Read model config file 
    with open(modelConfig_filename, "r") as f:
        try:
           model_config = yaml.load(f, Loader = yaml.FullLoader)
        except yaml.error.YAMLError as e:
            logger.error("Error while loading model configuration from %s", modelConfig_filename)
        else:
            logger.info("Model configuration file loaded from %s", modelConfig_filename)


    # ----------------------------------------------------------------
    # Download clean data csv file from S3 bucket
    # ----------------------------------------------------------------
    cleanData_filename = "/tmp/clean_data.csv"

    # Download file from s3
    logger.info("**Downloading clean data from S3**")
    dataKey = model_config.get("run_config")["clean_data_key"]
    logger.info("Data key: %s", dataKey)
    bucket.download_file(dataKey, cleanData_filename)
    logger.info("**Clean data downloaded from S3 to %s **", cleanData_filename)
    

    # Read clean data 
    logger.info("Reading clean data into pandas dataframe")
    data = pd.read_csv(cleanData_filename)
    logger.info("Clean data read into pandas dataframe")
    


    # ----------------------------------------------------------------
    # Train model, predict and evaluate
    # ----------------------------------------------------------------
    # Convert results folder to a Path
    logger.info("Creating results folder")
    au.create_folder_in_tmp('results')
    logger.info("Folder results created")
    results_dir = Path("/tmp/results/") 

    # Split data into train/test set and train model based on config; save each to disk
    logger.info("** Starting model training **")
    tmo, train, test, cv_result = tm.train_model(data,  **model_config["train_model"])
    logger.info("** Finished model training **")
    
    logger.info("** Saving training data to local folder **")
    tm.save_data(train, test, cv_result, results_dir)
    logger.info("** Saved training data to local folder %s **", results_dir)

    logger.info("** Saving tmo to local folder **")
    tm.save_model(tmo, results_dir / "tmo.pkl")
    logger.info("** Saved tmo to local folder %s **", results_dir)


    # Score model on test set; save scores to disk
    logger.info("** Sarting model scoring **")
    scores = sm.score_model(test, tmo, **model_config["score_model"])
    logger.info("** Finished model scoring **")

    logger.info("** Saving scores to local folder **")
    sm.save_scores(scores, results_dir / "scores.csv")
    logger.info("** Saved scores to local folder %s **", results_dir)


    # Evaluate model performance metrics; save metrics to disk
    logger.info("** Sarting model evaluation **")
    metrics = ep.evaluate_performance(scores)
    logger.info("** Finished model evaluation **")
    
    ep.save_metrics(metrics, results_dir / "metrics.yaml")
    logger.info("** Saved evaluation metrics to local folder %s **", results_dir)

    # ----------------------------------------------------------------
    # Upload artifacts to S3 folder
    # ----------------------------------------------------------------
    
    # Upload artifacts
    logger.info("** Uploading artifacts to S3 **")
    s3_uris = au.upload_artifacts(results_dir, model_config.get("aws"))
    logger.info("** Artifacts uploaded to S3 bucket. **")
    
    
    # ----------------------------------------------------------------
    # Return results
    # ----------------------------------------------------------------
    
    logger.info("**TRAINING DONE, returning results**")

    output = {"s3_uris": s3_uris}
    #
    # respond in an HTTP-like way, i.e. with a status
    # code and body in JSON format:
    #
    return {
      'statusCode': 200,
      'body': json.dumps(output)
    }
    
  except Exception as err:
    print("**ERROR**")
    print(str(err))
    
    return {
      'statusCode': 400,
      'body': json.dumps(str(err))
    }
