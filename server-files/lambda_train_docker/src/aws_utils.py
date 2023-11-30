"""
This module provides functions for uploading the generated artifacts to an S3 bucket. 
If allowed by the user, the process will create the S3 bucket if it doesn't exist.  
"""
import logging
import sys
import os
from pathlib import Path

from typing import List, Union, Dict
import boto3
from botocore.exceptions import BotoCoreError, ClientError

# Set logger
logger = logging.getLogger(__name__)


def upload_artifacts(local_dir: Union[Path, str], aws_config: Dict[str, str]) -> List[str]:
    """
    Uploads all files in a local directory to an S3 bucket, handling any errors encountered
    during the upload process.

    Args:
    - local_dir (Path or str): The local directory containing the files to upload.
    - aws_config (dict): A dictionary containing AWS configuration such as 'bucket_name' and 'prefix'.

    Returns:
    - s3_uris (list): A list of S3 URIs for the uploaded files. In case of an error, the list will
                      contain the URIs of the files that were successfully uploaded before the error occurred.
    """
    # --- Get files to upload ---
    # Ensure local_dir is a Path object
    local_dir = Path(local_dir)
    
    # Collect the names of all files in the directory
    files_to_upload = [f for f in local_dir.glob('*') if f.is_file()]
    logger.info("Files to upload: %s", files_to_upload)

    # --- Set S3 configuration ---
    logger.info("Setting S3 configuration.")
    
    # S3 client
    s3 = boto3.client('s3')
    
    # The S3 URIs that will be returned
    s3_uris = []
    
    # S3 bucket and folder details from aws_config
    logger.debug("Getting AWS configuration")
    bucket_name = aws_config['bucket_name']
    logger.debug("    bucket_name: %s", bucket_name)
        
    s3_folder = aws_config['prefix']
    logger.debug("    folder: %s", s3_folder)
    logger.info("Finish setting S3 configuration.")
        

    # --- Iterate over the files and upload each one ---
    for file_path in files_to_upload:
        # Define the S3 key (i.e., 's3_folder/filename')
        s3_key = f"{s3_folder}/{file_path.name}"
        logger.debug("s3_key: %s", s3_key)
        
        # Upload the file & add URI to list
        try:
            s3.upload_file(Filename=str(file_path), Bucket=bucket_name, Key=s3_key)
        except (ClientError, BotoCoreError) as e:
            logger.error("Failed to upload %s to S3. Error: %s", file_path, e)
            raise Exception(f"Failed to upload {file_path} to S3") from e
        else:
            s3_uri = f"s3://{bucket_name}/{s3_key}"
            logger.info("File %s uploaded. S3 URI: %s", s3_key, s3_uri)
        
        s3_uris.append(s3_uri)

    logger.info("Finished uploading files to S3")
        
    return s3_uris


def create_folder_in_tmp(folder_name: str) -> None:
    """
    Creates a directory named `folder_name` within the /tmp directory. If the directory already
    exists, no action is taken. This function is useful in environments like AWS Lambda where
    the /tmp directory is used for temporary storage.

    Args:
    - folder_name (str): The name of the folder to create within the /tmp directory.
    """
    # Set path
    path = f"/tmp/{folder_name}"
    
    try:
        # Create a new directory if it does not exist
        os.makedirs(path, exist_ok=True)
        logger.info(f"Directory '{folder_name}' created in /tmp")
    except OSError as error:
        logger.error(f"Creation of the directory {path} failed. Error: %s", error)