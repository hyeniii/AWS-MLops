import io
import os
import zipfile
from configparser import ConfigParser
import requests
import boto3

def lambda_handler(event, context):
    # source_url = "https://archive.ics.uci.edu/static/public/555/apartment+for+rent+classified.zip"
    source_url = event["source_url"]

    try:
        print("Begin downloading the files...")
        # Download the file from the internet
        r = requests.get(source_url)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        zipfile_path = "/tmp/"
        z.extractall(zipfile_path)

        zip_files = os.listdir(zipfile_path)
        print(zip_files)
        print("Downloaded files successfully.")

        # Unzip the file
        # for zip_file in zip_files:
        #     print(f"Unzipping file {zip_file}.\n")
        #     try:
        #         with py7zr.SevenZipFile(zipfile_path + zip_file, mode='r') as archive:
        #             # Extract all the contents to the specified directory
        #             archive.extract(zipfile_path)
        #     except Exception as err:
        #         print(f"An error has occured during unzipping the file: {err}.")

        # data_files = [file for file in os.listdir(zipfile_path) if file.endswith(".csv")]
        
        for file in zip_files:
            if file.endswith("100K.7z"):
                os.rename(zipfile_path + file, zipfile_path + "train.7z")
            if file.endswith("10K.7z"):
                os.rename(zipfile_path + file, zipfile_path + "test.7z")
        zip_files = [file for file in os.listdir(zipfile_path) if file.endswith(".7z")]
        print(zip_files)

        #
        # setup AWS S3 access based on config file:
        #
        config_file = 'config.ini'
        s3_profile = 'aws-mlops-s3readwrite'

        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
        boto3.setup_default_session(profile_name=s3_profile)
        
        configur = ConfigParser()
        configur.read(config_file)
        bucketname = configur.get('s3', 'bucket_name')
        print(f"The bucketname is {bucketname}.")
        
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucketname)
        print(s3)

        # Uploading the zipfiles to s3
        for file in zip_files:
            print(f"Uploading {file} to s3 bucket {bucketname}.")
            bucket.upload_file(zipfile_path +  file, file)
        print(f"Uploaded files to s3 bucket {bucketname} successfully.")

        return {
            'statusCode': 200,
            'body': 'Files downloaded and uploaded to S3 successfully.'
        }

    except Exception as e:
        print(f"Execution failed with error: {e}")
        return {
            'statusCode': 500,
            'body': str(e)
        }