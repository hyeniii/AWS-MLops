#
# Client-side python app for Final Project, this time working with
# web service, which in turn uses AWS S3 ato implement
# a simple ML Model for rental price prediction and apartment description generation.
#
# Final Project for CS 310
#
# Authors:
#   YOUR NAME
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
from configparser import ConfigParser

import requests  # calling web service
# import json  # relational-object mapping

import matplotlib.pyplot as plt
import matplotlib.image as img

import streamlit as st

###################################################################
#
# classes
#
# class User:
#   userid: int  # these must match columns from DB table
#   email: str
#   lastname: str
#   firstname: str
#   bucketfolder: str

###################################################################
#
# Make Prediction
#

def make_prediction(baseurl, input_data) -> float:
  """
  Make Prediction of rental price based on users
  
  Parameters
  ----------
  baseurl: baseurl for web service
  input_data: Input data for making prediction
  
  Returns
  -------
  Predicted Rental Price (rounded to 2 decimals)
  """
  
  try:
    #
    # build the data packet:
    #
    data = {
      "bathrooms": input_data["bathrooms"],
      "bedrooms": input_data["bedrooms"],
      "has_photos": input_data["bedrooms"],
      "pets_allowed": input_data["pets_allowed"],
      "square_feet": input_data["square_feet"],
      "cityname": input_data["cityname"]
    }

    #
    # call the web service:
    #
    api = '/makeprediction'
    url = baseurl + api

    res = requests.put(url, json=data)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return

    #
    # success, extract userid:
    #
    body = res.json()

    predicted_price = body["predicted_price"]
    message = body["message"]

    print(f"The rental price is predicted to be ${predicted_price}.")

  except Exception as e:
    logging.error("make_prediction() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

###################################################################
#
# Add to existing CSV
#
def add_data(baseurl, input_data):
  """
  Appends new rows to the existing CSV
  
  Parameters
  ----------
  baseurl: baseurl for web service
  input_data: Data inputted by the user
  
  Returns
  -------
  nothing
  """

  try:
    #
    # build the data packet:
    #
    data = {
      "bathrooms": input_data["bathrooms"],
      "bedrooms": input_data["bedrooms"],
      "has_photos": input_data["bedrooms"],
      "pets_allowed": input_data["pets_allowed"],
      "square_feet": input_data["square_feet"],
      "cityname": input_data["cityname"]
    }

    #
    # call the web service:
    #
    api = '/add_data'
    url = baseurl + api

    res = requests.put(url, json=data)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return

    #
    # success, extract userid:
    #
    body = res.json()

    # predicted_price = body["predicted_price"]
    message = body["message"]

    print(f"The data has been successfully input by the user.")

  except Exception as e:
    logging.error("add_data() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

###################################################################
#
# Add to existing CSV
#
def make_description(baseurl, input_data):
  """
  Uses Langchain to make new summary based on the data
  
  Parameters
  ----------
  baseurl: baseurl for web service
  input_data: Data inputted by the user
  
  Returns
  -------
  nothing
  """

  try:
    #
    # build the data packet:
    #
    data = {
      "bathrooms": input_data["bathrooms"],
      "bedrooms": input_data["bedrooms"],
      "has_photos": input_data["has_photos"],
      "pets_allowed": input_data["pets_allowed"],
      "square_feet": input_data["square_feet"],
      "cityname": input_data["cityname"]
    }

    #
    # call the web service:
    #
    api = '/make_description'
    url = baseurl + api

    res = requests.put(url, json=data)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return

    #
    # success, extract userid:
    #
    body = res.json()

    predicted_description = body["description"]
    message = body["message"]

    print(f"The description has been {message}ly generated by user. Below is the description:\n\n")
    print(predicted_description)

  except Exception as e:
    logging.error("make_description() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

#########################################################################
# main
#

st.set_page_config(
    page_title="Go To Rental Wizard",
    page_icon="👍",
)

st.title('** Let\'s get started! **')
st.sidebar.success("Let's get started.")
st.header('Please input these details.')
bathrooms = st.number_input("Please enter the number of bedrooms.")
bedrooms = st.number_input("Please enter the number of bathrooms.")
has_photos = st.selectbox("Do you have photos?", ("Yes", "No"))
pets_allowed = st.selectbox("Are pets allowed?", ("Yes", "No"))
square_feet = st.number_input("Please enter the area in square feet.")
cityname = st.text_input("Please enter the name of the city.")
print(cityname)


# eliminate traceback so we just get error message:
sys.tracebacklimit = 0

# #
# # what config file should we use for this session?
#
config_file = 'rental-wizard-client-config.ini'

# print("What config file to use for this session?")
# print("Press ENTER to use default (photoapp-client-config.ini),")
# print("otherwise enter name of config file>")
# s = input()

# if s == "":  # use default
#   pass  # already set
# else:
#   config_file = s

# #
# # does config file exist?
# #
# if not pathlib.Path(config_file).is_file():
#   print("**ERROR: config file '", config_file, "' does not exist, exiting")
#   sys.exit(0)

# #
# # setup base URL to web service:
# #
# configur = ConfigParser()
# configur.read(config_file)
# baseurl = configur.get('client', 'webservice')

# # print(baseurl)

# #
# # main processing loop:
# #
# cmd = prompt()

# while cmd != 0:
#   #
#   if cmd == 1:
#     stats(baseurl)
#   elif cmd == 2:
#     users(baseurl)
#   elif cmd == 3:
#     assets(baseurl)
#   elif cmd == 4:
#     print("Enter asset id>")
#     asset_id = input()
#     download(baseurl, asset_id)
#   elif cmd == 5:
#     print("Enter asset id>")
#     asset_id = input()
#     download_and_display(baseurl, asset_id)
#   elif cmd == 6:
#     bucket(baseurl)
#   else:
#     print("** Unknown command, try again...")
#   #
#   cmd = prompt()

# #
# # done
# #
# print()
# print('** done **')
