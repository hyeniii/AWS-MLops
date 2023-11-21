import json
import boto3
import os
import pickle
import joblib
import io
import logging
import yaml
import pandas as pd 
from pathlib import Path
import numpy as np
import prediction_utils as pu
from configparser import ConfigParser

# Set logger
logger = logging.getLogger(__name__)

def input_type_checker(input_dict):
  mapper = {
      "bathrooms": int,
      "bedrooms": int,
      "amenities": lambda x: [str(item) for item in x],
      "has_photos": str,
      "dogs_allowed": str,
      "cats_allowed": str,
      "square_feet": int,
      "address": str,
      "cityname": str,
      "state": str,
      "zipcode": int
    }
   # Iterate over the items in the input dictionary
  for key, value in input_dict.items():
      # Cast to the type specified in mapper if the key is in the mapper
      if key in mapper:
          try:
            input_dict[key] = mapper[key](value)
          except ValueError as e:
              raise ValueError(f"Invalid type for {key}: {e}")
  return input_dict
   

def lambda_handler(event, context):
  try:
    os.chdir('lambda_predict_price')
    print("**STARTED**")
    
    # ----------------------------------------------------------------
    # setup AWS S3 access based on config file:
    # ----------------------------------------------------------------
    config_file = 'config.ini' 
    s3_profile = 'aws-mlops-s3readonly'
    
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
    model_dict = pu.get_model_dict(bucketname, "modeling") # NOTE: SHOULD WE GET THIS PREFIX FROM THE MODEL CONFIG FILE? 


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
    if not event:
        # Raise error if input data does not exist
        raise ValueError("No input data provided for prediction.")
    else:
      # Get input data from event and convert to pandas df
      input_data_dict = input_type_checker(event)
      df = pd.DataFrame([input_data_dict]) 


    # ----------------------------------------------------------------
    # Cleand and get features 
    # ----------------------------------------------------------------    
    # features = pd with the cleanned features.
    df['n_amenities'] = df.amenities.apply(len)
    # df['price_per_sq_feet'] = df.price / df.square_feet

    object_key = 'modeling_artifacts/new_split/encoder.joblib'
    local_file_path = '/tmp/encoder.joblib'

    # Download the file
    bucket.download_file(object_key, local_file_path)
    encoder = joblib.load(local_file_path)
    encoded_data = encoder.transform(df[['fee', 'has_photo', '']])
    encoded_df = pd.DataFrame(encoded_data.toarray(), columns=model.get_feature_names_out())

    # ----------------------------------------------------------------
    # Make prediction
    # ----------------------------------------------------------------
    # Get prediction for selected features

    if hasattr(model, 'feature_names_in_'):
      features = model.feature_names_in_
    try:
        pred_price = model.predict(encoded_df[features])
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
input_data = {
      "bathrooms": 2,
      "bedrooms": 2,
      "amenities": ['Gym'],
      "has_photo": 'Yes',
      "dogs_allowed": 'Yes',
      "cats_allowed": 'no',
      "fee": "Yes",
      "square_feet": 500,
      "address": 'test address',
      "cityname": 'Evanston',
      "state": 'IL',
      "zipcode": 60201
    }

lambda_handler(input_data,0)