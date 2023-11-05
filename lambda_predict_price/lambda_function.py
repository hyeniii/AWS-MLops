import json
import boto3
import os
import pickle

import logging
import yaml
import pandas as pd 
from pathlib import Path

import prediction_utils as pu 

from configparser import ConfigParser

# Set logger
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
  try:
    print("**STARTED**")
    
    # ----------------------------------------------------------------
    # setup AWS S3 access based on config file:
    # ----------------------------------------------------------------
    config_file = 'config.ini' 
    s3_profile = 's3readonly'
    
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
    boto3.setup_default_session(profile_name=s3_profile)
    
    configur = ConfigParser()
    configur.read(config_file)
    bucketname = configur.get('s3', 'bucket_name')
    
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucketname)


    # ----------------------------------------------------------------
    # extract tmo file 
    # ----------------------------------------------------------------
    # Get model dictionary for most recent model.
    model_dict = pu.get_model_dict(bucket, "modeling") # NOTE: SHOULD WE GET THIS PREFIX FROM THE MODEL CONFIG FILE? 


    # ----------------------------------------------------------------
    # Download tmo file from S3 to local filesystem:
    # ----------------------------------------------------------------
    # Set local name for model config file
    tmo_filename = "/tmp/tmo.pkl"

    # Download file from s3
    logger.info("**Downloading model pikle file from S3**")
    bucket.download_file(model_dict["tmo_key"], tmo_filename)
    
    # load pickle file
    model = pu.load_model(tmo_filename)
  

    # ----------------------------------------------------------------
    # Extract input data from event
    # ----------------------------------------------------------------
    if 'input_data' not in event:
        # Raise error if input data does not exist
        raise ValueError("No input data provided for prediction.")
    else:
      # Get input data from event and convert to pandas df
      input_data_dict = event['input_data']
      input_data = pd.DataFrame([input_data_dict])  


    # ----------------------------------------------------------------
    # Cleand and get features 
    # ----------------------------------------------------------------

    # TODO 
    # features = pd with the cleanned features. 


    # ----------------------------------------------------------------
    # Make prediction
    # ----------------------------------------------------------------
    # Get prediction for selected features
    try:
        pred_price = model.predict(features)
    except ValueError as err:
        logger.warning("Error with the feature shape or values. Setting predicted class and" +
                        " probability to NA. Error: %s", err)
        return np.nan

    
    print("**PREDICTION DONE, returning results**")


    #
    # respond in an HTTP-like way, i.e. with a status
    # code and body in JSON format:
    #
    return {
      'statusCode': 200,
      'body': json.dumps({"pred_price": pred_price})
    }
    
  except Exception as err:
    print("**ERROR**")
    print(str(err))
    
    return {
      'statusCode': 400,
      'body': json.dumps(str(err))
    }
