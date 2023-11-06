"""
This module provides functions for uploading the generated artifacts to an S3 bucket. 
If allowed by the user, the process will create the S3 bucket if it doesn't exist.  
"""
import logging
import sys
from pathlib import Path

import typing
import boto3
import botocore

# Set logger
logger = logging.getLogger(__name__)


def upload_artifacts(artifacts: Path, aws_config: dict) -> typing.List[str]:
    """
    Upload all the artifacts in the specified directory to an S3 bucket.

    Args:
        artifacts_dir: A Path object pointing to the directory containing all the artifacts
                       from a given experiment.
        aws_config: A dictionary containing the configuration required to upload artifacts 
                    to S3.
                    - 'bucket_name': The name of the S3 bucket to upload the artifacts to.
                    - 'prefix': The S3 object key prefix to prepend to the uploaded artifact
                      objects.
    Returns:
        A list of S3 URIs for each file that was uploaded.
    """
    # Create an S3 client using the default credentials chain
    try:
        session = boto3.Session()
        s3_client = session.client("s3")
    except botocore.exceptions.ClientError as err:
        logger.error("Error creating S3 client. The process can't continue with the upload of " +
                     "artifacts to S3 bucket. Error: ", err)

    # Get bucket name and list of existing buckets
    bucket_name = aws_config["bucket_name"]
    list_buckets = [bucket["Name"] for bucket in s3_client.list_buckets()["Buckets"]]

    # If bucket doesn't exist log error and return no files. 
    if bucket_name not in list_buckets:
        logger.error("S3 bucket %s does not exist. Create the corresponding bucket on your AWS " +
                    "account before running the project.", bucket_name)
        return ["S3 bucket does not exist. No files uploaded."]

    # Get a list of all files in the artifacts
    files = artifacts.glob("**/*")

    # Iterate through each file in the local folder
    s3_uris = []

    for file_name in files:
        # Skip directories
        if file_name.is_dir():
            continue

        # Construct the S3 key name for the file
        s3_key = Path(aws_config["prefix"]).joinpath(file_name.relative_to(artifacts))

        # Create the S3 bucket folders if they don't already exist to map structure
        if s3_key.parent != Path(aws_config["prefix"]):
            try:
                s3_client.put_object(Bucket=bucket_name, Key=str(s3_key.parent) + "/")
            except botocore.exceptions.BotoCoreError as err:
                logger.warning("Could not create folder %s. Files in that folder will not be " +
                               "stored. Error: %s", str(s3_key.parent), err)
                logger.debug("Folder %s created in S3 bucket %s.", s3_key.parent, bucket_name)

        # Upload files
        try:
            # Upload file to specified S3 bucket
            s3_client.upload_file(str(file_name), bucket_name, str(s3_key))
        except botocore.exceptions.BotoCoreError as err:
            logger.warning("Error uploading file %s to S3. The process will continue without " +
                           "uploading this file. Error: %s", file_name, err)
        else:
            # Append S3 URI to list
            s3_uris.append(f"s3://{bucket_name}/{s3_key}")
            logger.debug("File %s uploaded to S3 bucket %s.", file_name, bucket_name)

    # Function output
    return s3_uris

def write_list_files(s3_uris: list[str], save_path: Path) -> None:
    """
    Writes list of s3 URIs of uploaded files.

    Args:
        s3_uris: A list containing the URI of uploaded files.
        save_path: A Path object representing the local path to write data to.
    """
    # Convert figs_list to a string
    uris_str = "\n".join(str(fig) for fig in s3_uris)

    # Write content to the file
    try:
        with open(save_path, "w", encoding = 'utf-8') as file:
            file.write(uris_str)
        logger.info("URI's of stored files written succesfully to %s", save_path)
    except FileNotFoundError:
        logger.warning("File %s not found. The process will continue without saving the list of " +
                       "URI's. Please provide a valid file location to save the information to.",
                       save_path)
    except PermissionError:
        logger.warning("The process does not have the necessary permissions to create or write " +
                       "to the file %s. The process will continue without saving the list of " +
                       "URI's.", save_path)
    except IsADirectoryError:
        logger.warning("The specified path %s is a directory, not a file. " +
                       "The process will continue without saving the list of URI's.", save_path)
    except Exception as err:
        logger.warning("An error occurred when saving to file %s. The process will continue " +
                       "without saving the list of URI's. Error: %s", save_path, err)
