import json
import boto3
import os
import joblib
import logging
import yaml
import pandas as pd 
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
      "fee": str,
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
            if isinstance(input_dict[key], str):
                    input_dict[key] = input_dict[key].lower()
          except ValueError as e:
              raise ValueError(f"Invalid type for {key}: {e}")
  return input_dict
   

def lambda_handler(event, context):
  try:
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

    with open('inference_config.yaml', 'r') as file:
       inf_config = yaml.safe_load(file)
    bucketname = configur.get('s3', 'bucket_name')
    
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucketname)
    print("Connected to S3")

    # ----------------------------------------------------------------
    # extract tmo file 
    # ----------------------------------------------------------------
    # Get model dictionary.
    model_dict = pu.get_model_dict(bucketname, "modeling_artifacts/")


    # ----------------------------------------------------------------
    # Download tmo file from S3 to local filesystem:
    # ----------------------------------------------------------------

    # Download file from s3
    logger.info("**Downloading model pikle file from S3**")
    bucket.download_file(model_dict["tmo_key"], inf_config['model_save_path'])
    print("Downloaded model pkl file")
    
    # load pickle file
    model = pu.load_model(inf_config['model_save_path'])
    print("Loaded model pkl file")
  

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
      print("Prediction input valid")


    # ----------------------------------------------------------------
    # Cleand and get features 
    # ----------------------------------------------------------------    


    # Download the file
    bucket.download_file(inf_config['encoder_s3_key'], inf_config['encoder_save_path'])
    encoder = joblib.load(inf_config['encoder_save_path'])
    print("Loaded encoder")

    # Transform the categorical data
    encoded_data = encoder.transform(df[encoder.feature_names_in_.tolist()])

    # Convert the encoded data to DataFrame
    encoded_df = pd.DataFrame(encoded_data, columns=encoder.get_feature_names_out())

    # Merge the encoded categorical data with the numerical data
    df = pd.concat([df, encoded_df], axis=1)

    df['n_amenities'] = df.amenities.apply(len)
    print("Created new features")

    # ----------------------------------------------------------------
    # Make prediction
    # ----------------------------------------------------------------
    # Get prediction for selected features

    if hasattr(model, 'feature_names_in_'):
      features = model.feature_names_in_.tolist()
    try:
        pred_price = round(model.predict(df[features])[0],2)
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
