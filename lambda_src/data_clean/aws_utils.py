import os
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def s3_client(config):
    try:
        # Get values from the config file
        s3 = boto3.client(
        's3',
        aws_access_key_id= config.get('aws-mlops-s3readwrite', 'aws_access_key_id'),
        aws_secret_access_key= config.get('aws-mlops-s3readwrite', 'aws_secret_access_key'),
        region_name= config.get('aws-mlops-s3readwrite', 'region_name')
        )
    except Exception as e:
        print(e)
    return s3

def s3_get_obj(s3_client, config, key, local_fn):
    try:
        # The bucket name and object (file) key
        bucket_name = config.get('s3', 'bucket_name')
        # store in /tmp so it is writable
        local_file_path = os.path.join('/tmp', local_fn)

        # Get the object from S3
        s3_client.download_file(Bucket=bucket_name, Key=key, Filename=local_file_path)
        logger.info(f"File {key} downloaded to {local_file_path}.")
        # res = s3_client.get_object(Bucket=bucket_name,Key=key)
        # logger.info(f"File {key} retrieved.")
        # Read the object's content into a DataFrame

    except Exception as e:
            # Handle other possible exceptions
        logger.error(f"Error downloading {key}: {e}", exc_info=True)
        return None
    return local_file_path

def s3_upload(s3_client, config, key, content):
    try:
        # The bucket name and object (file) key
        bucket_name = config.get('s3', 'bucket_name')

        # Get the object from S3
        response = s3_client.put_object(Bucket=bucket_name, Key=key, Body=content)
        logger.info(f"File {key} uploaded to bucket {bucket_name}.")
    except Exception as e:
        logger.error(f"Error uploading {key}: {e}", exc_info=True)
        return None
    return response