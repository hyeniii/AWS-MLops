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
from datetime import datetime

import requests  # calling web service
# import json  # relational-object mapping

import streamlit as st

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
    # build the data packet:
    ###################################################################################
    data = json.dumps(input_data)
    print(data)

    # headers = {
    # "Content-Type": "application/json"
    # }

    ###################################################################################
    # call the web service:
    ###################################################################################
    api = '/train_pipeline'
    url = baseurl + api

    res = requests.post(url, json=data) # headers=headers, 
    print(res.json())

    ###################################################################################
    # let's look at what we got back:
    ###################################################################################
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      body = res.json()
      if res.status_code == 400:  # we'll have an error message
        print("Error message:", body["body"])
      #
      return body

    #
    # success:
    #
    body = res.json()
    print(body)

    if body["statusCode"] == 200:
        print("The training is successfully completed.")
        return body

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

ingest_data = st.selectbox("Do you want to ingest data (Recommended for training the first time)?", ("Yes", "No"))

if ingest_data == "Yes":
    ingest_data = "true"
else:
    ingest_data = "false"

print(ingest_data)

data_url = str(configur.get('source', 'url'))

model_config = str(configur.get('modelConfig', 'modelConfigKey'))

pipeline_data = "\"ingestData\": {},\"source_url\": \"{}\",\"modelConfigKey\": \"{}\"".format(ingest_data, data_url, model_config)
pipeline_data = "{"+pipeline_data+"}"

# pipeline_data = {"ingestData": ingest_data,
#                 "source_url": data_url,
#                 "modelConfigKey": model_config}

print(pipeline_data)

arn = configur.get('train_pipeline', 'stateMachineArn')

time_now = datetime.now()
pipeline_name = "train-pipeline-"+time_now.strftime('%Y-%m-%d_%H-%M-%S')

input_data = {"input": pipeline_data,
            "name": pipeline_name,
            "stateMachineArn": arn
            }

print(input_data)

#########################################################################
# setup base URL to web service:
#
baseurl = configur.get('client', 'webservice')

print(baseurl)
print("Lets train the model.....")

if st.button("Train model."):
  train_result = train_model(baseurl, input_data)
  print(train_result)
  if train_result['statusCode'] == 200:
    st.write("Training has been completed successfully.")
  else:
    print("There was an error during training.")
    st.write(train_model["body"])
else:
  st.write('Sorry, the specs you have shared are not valid. Try again.')