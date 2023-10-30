import os
import urllib.request
import boto3

s3 = boto3.client('s3')

def lambda_handler(event, context):
    source_url = "https://archive.ics.uci.edu/static/public/555/apartment+for+rent+classified.zip" 
    s3_bucket = "aws-mlops-project"
    s3_key = "raw/data.zip"

    try:
        # Download the file from the internet
        response = urllib.request.urlopen(source_url)
        data = response.read()  # Read the response data as bytes

        # Upload the downloaded file to S3
        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=data)

        return {
            'statusCode': 200,
            'body': 'File downloaded and uploaded to S3 successfully.'
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }

