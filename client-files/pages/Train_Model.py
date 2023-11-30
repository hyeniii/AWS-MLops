#
# Client-side python app for Final Project, this time working with
# web service, which in turn uses AWS S3 ato implement
# a simple ML Model for rental price prediction and apartment description generation.
#
# Final Project for CS 310
#
# Authors:
#   Sharika Mahadevan, Hye Won Hwang, Alejandra Lelo de Larrea Ibarra
#   Northwestern University
#   CS 310
#

###################################################################
#
# Importing packages
#

import os
import pathlib
import logging
import sys
import base64
import json
from configparser import ConfigParser
from datetime import datetime, timezone
import boto3

import requests  # calling web service

import streamlit as st

###################################################################
#
# List all files in S3 folder
#
def list_files(bucket_name, prefix):
    """List files in specific S3 URL"""
    client = boto3.client('s3')
    response = client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    files = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'] != prefix]
    return files

###################################################################
#
# Train the model
#

def train_model(baseurl, input_data) -> None:
  """
  To Train model for rental price predictions
  
  Parameters
  ----------
  baseurl: baseurl for web service
  input_data: Input data for Training Pipeline
  
  Returns
  -------
  None
  """
  
  try:
    ###################################################################################
    # call the web service:
    ###################################################################################
    api = '/train_pipeline'
    url = baseurl + api

    res = requests.post(url, json=input_data) # headers=headers, 
    print("Response from webservice: ")
    print(res.json())

    # Get response body
    body = res.json()

    ###################################################################################
    # let's look at what we got back:
    ###################################################################################
    if "executionArn" not in body.keys():
      #
      # failed:
      #
      print("url: " + url)
      print(f"Execution of step function failed.")

      # Add status 400 to response
      response = {'statusCode': 400}
      response.update(body)
    else:
    #
    # success:
    #
      print("Successfully triggered training pipeline.")

      # Add status 200 to response
      response = {'statusCode': 200}
      response.update(body)
    
    return response

  except Exception as e:
    print("train_pipeline() failed:")
    print("url: " + url)
    print(e)
    return

# eliminate traceback so we just get error message:
sys.tracebacklimit = 0

#########################################################################
# What config file should we use for this session?
#
config_file = 'client-files/rental-wizard-client-config.ini'
configur = ConfigParser()
configur.read(config_file)

#########################################################################
# main
#

st.set_page_config(
    page_title="Welcome to Employee Page.",
    page_icon="🚀",
)

st.title('** Let\'s get started! **')
st.sidebar.success("Employee Page: Train the Model.")
st.header('Please input these details.')

# --- Get user inputs --- 
# Training or retraining? 
ingest_data = st.selectbox("Do you want to ingest data (Recommended for training the first time)?", ("---Select an option--", "Yes", "No"))

if ingest_data == "Yes":
    ingest_data = "true"
else:
    ingest_data = "false"

print(f"Ingest data: {ingest_data}")

# Source of data
data_url = str(configur.get('source', 'url'))
print(f"Data URL: {data_url}")

# Model Config file
#model_config = str(configur.get('modelConfig', 'modelConfigKey'))
configFilesList = ["---Select a file---"]
configFilesList.extend(list_files("aws-mlops-project", "config/"))
print("class config file list:" )
print(configFilesList)
model_config = st.selectbox("Select a model config. file from the list of current files in S3:", configFilesList) 
print(f"Model config key: {model_config}")

# Dictionary of user inputs 
input_data = {"ingestData": ingest_data,
                 "source_url": data_url,
                 "modelConfigKey": model_config}
print("Input data to be passed: ")
print(input_data)

#########################################################################
# setup base URL to web service:
#
baseurl = configur.get('client', 'webservice')

print(f"Base URL: {baseurl}")
print("Lets train the model.....")

if st.button("Train model."):

  # Trigger step function
  train_result = train_model(baseurl, input_data)
  
  print("Train results: ")
  print(train_result)

  # If trigger is succesful, return info of state machine 
  if train_result['statusCode'] == 200:
    st.write("Model training execution has started successfully.")
    startTime = datetime.utcfromtimestamp(train_result['startDate']).strftime("%Y-%m-%d %H:%M:%S")
    st.write(f"    Execution began at {startTime} UTC.")
    st.write("    You can track the execution status in this ARN:")
    st.write(f"    {train_result['executionArn']}")
  # If trigger is not sucessfull return body with error/problem message
  else:
    print("There was an error during training. Error:")
    print("train_result")
    st.write("There was an error during training. Error: ")
    st.write(train_result)
else:
  st.write('Select model specifications to start training.')