import json
import boto3
import os

import logging
import yaml
import pandas as pd 

import train_model as tm
import score_model as sm
import evaluate_performance as ep

from configparser import ConfigParser

# Set logger
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
  try:
    print("**STARTED**")
    
    #
    # setup AWS S3 access based on config file:
    #
    config_file = 'aws_config.ini' #NEED TO ADD THIS FILE.
    s3_profile = 's3readwrite' # ASK IF WE CAN PASS THIS AS ARGUMENTS OF THE FUNCTION. 
    
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
    boto3.setup_default_session(profile_name=s3_profile)
    
    configur = ConfigParser()
    configur.read(config_file)
    bucketname = configur.get('s3', 'bucket_name')
    
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucketname)

    #
    # extract model config file key from event: could be a parameter
    # or could be part of URL path ("pathParameters"):
    #
    if "modelConfigKey" in event:
      modelConfigKey = event["modelConfigKey"]
    elif "pathParameters" in event:
      if "modelConfigKey" in event["pathParameters"]:
        modelConfigKey = event["pathParameters"]["modelConfigKey"]
      else:
        raise Exception("requires modelConfigKey parameter in pathParameters")
    else:
        raise Exception("requires modelConfigKey parameter in event")
        
    logger.info("modelConfigKey:", modelConfigKey)
    

    # ----------------------------------------------------------------
    # download model config file from S3 to local filesystem:
    # ----------------------------------------------------------------
    # Set local name for model config file
    modelConfig_filename = "/tmp/model_config.yaml"

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
    bucket.download_file(model_config.get("run_config")["clean_data_key"], cleanData_filename)

    # Read clean data 
    data = pd.read_csv(cleanData_filename)


    # ----------------------------------------------------------------
    # Train model, predict and evaluate
    # ----------------------------------------------------------------
    # Split data into train/test set and train model based on config; save each to disk
    tmo, train, test, cv_results = tm.train_model(data,  **model_config["train_model"])
    tm.save_data(train, test, cv_result, "/results/")
    tm.save_model(tmo, "/results/tmo.pkl")

    # Score model on test set; save scores to disk
    scores = sm.score_model(test, tmo, **model_config["score_model"])
    sm.save_scores(scores, "/results/scores.csv")

    # Evaluate model performance metrics; save metrics to disk
    metrics = ep.evaluate_performance(scores)
    ep.save_metrics(metrics, "/results/metrics.yaml")

    
    print("**TRAINING DONE, returning results**")

    output: {"tmo": tmo, 
             "train": train, 
             "test": test, 
             "cv_results": cv_results, 
             "scores": scores, 
             "metrics": metrics}
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
