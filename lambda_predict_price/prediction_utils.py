"""
This module provides auxiliary functions to predict price of an apartment.
"""
import pickle
from pathlib import Path
import logging
import sys
import typing
import pandas as pd
import numpy as np
from botocore.exceptions import ClientError


# Set logger
logger = logging.getLogger(__name__)

def get_model_dict(bucket_name: str, artifacts_prefix: str) -> dict:
    """
    Retrieves the most recent model file from an AWS S3 bucket and creates a dictionary with
    the model name, key, and local path.

    Args:
        bucket_name (str): The name of the S3 bucket where the model files are stored.
        artifacts_prefix (str): The prefix of the S3 keys that identifies the model files.
        local_folder (Path): The local path where the model files will be stored after download.

    Returns:
        model_dict (dict): A dictionary containing the model name, S3 key, and local path.
    """
    s3_client = boto3.client('s3')
    
    try:
        # List all objects within the specified bucket and prefix
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=artifacts_prefix)
        if 'Contents' not in response:
            logger.error(f"Bucket {bucket_name} with prefix {artifacts_prefix} has no files.")
            sys.exit(1)

        # Filter out the .pkl files
        model_files = [obj for obj in response['Contents'] if obj['Key'].endswith('.pkl')]

        if not model_files:
            logger.error(f"Bucket {bucket_name} with prefix {artifacts_prefix} has no .pkl files.")
            sys.exit(1)

        # Sort the models by last modified date in descending order
        model_files.sort(key=lambda obj: obj['LastModified'], reverse=True)

        # Select the most recent model file
        latest_model = model_files[0]

        # Create the model dictionary
        model_dict = {
            'model_name': latest_model['Key'].split('/')[-1],
            'tmo_key': latest_model['Key']
        }

        return model_dict
    
    except ClientError as e:
        logger.error(f"Encountered an error accessing S3: {e}")
        sys.exit(1)



def load_model(model_file: str) -> typing.Any:
    """
    Download a model file from an AWS S3 bucket and load it into memory using pickle.

    Args:
        bucket_name (str): The name of the S3 bucket where the model file is stored.
        model_key (str): The key in the S3 bucket that identifies the model file.
        model_file (str): The local path where the downloaded model file will be stored.

    Returns:
        The deserialized model object, as returned by pickle.load.
    """
    # load pickle file
    try:
        model = pickle.load(open(model_file,'rb'))
    except FileNotFoundError:
        logger.error("Model %s not found. Application can't continue.", model_file)
        sys.exit(1)
    except pickle.UnpicklingError:
        logger.error("There was a problem unpickling the file. Application can't continue")
        sys.exit(1)
    else:
        logger.info("Model %s loaded into memory.", model_file)
    # Function output
    return model
