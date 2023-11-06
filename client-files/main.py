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

import requests  # calling web service
import jsons  # relational-object mapping

import uuid
import pathlib
import logging
import sys
import os
import base64

from configparser import ConfigParser

import matplotlib.pyplot as plt
import matplotlib.image as img

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
# stats
#
def stats(baseurl):
  """
  Prints out S3 and RDS info: bucket status, # of users and 
  assets in the database
  
  Parameters
  ----------
  baseurl: baseurl for web service
  
  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/stats'
    url = baseurl + api

    res = requests.get(url)
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
    # deserialize and extract stats:
    #
    body = res.json()
    #
    print("bucket status:", body["message"])
    print("# of users:", body["db_numUsers"])
    print("# of assets:", body["db_numAssets"])

  except Exception as e:
    logging.error("stats() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


###################################################################
#
# users
#
def users(baseurl):
  """
  Prints out all the users in the database
  
  Parameters
  ----------
  baseurl: baseurl for web service
  
  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/users'
    url = baseurl + api

    res = requests.get(url)

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
    # deserialize and extract users:
    #
    body = res.json()
    #
    # let's map each dictionary into a User object:
    #
    users = []
    for row in body["data"]:
      user = jsons.load(row, User)
      users.append(user)
    #
    # Now we can think OOP:
    #
    for user in users:
      print(user.userid)
      print(" ", user.email)
      print(" ", user.lastname, ",", user.firstname)
      print(" ", user.bucketfolder)

  except Exception as e:
    logging.error("users() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


#########################################################################
# assets
#
def assets(baseurl):
  """
  Prints out all the users in the database

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/assets'
    url = baseurl + api

    res = requests.get(url)

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
    # deserialize and extract assets:
    #
    body = res.json()
    #
    # let's map each dictionary into an Asset object:
    #
    assets_list = []
    for row in body["data"]:
      asset = jsons.load(row, Asset)
      assets_list.append(asset)
    #
    # Now we can think OOP:
    #
    for asset in assets_list:
      print(asset.assetid)
      print(" ", asset.userid)
      print(" ", asset.assetname)
      print(" ", asset.bucketkey)

  except Exception as e:
    logging.error("assets() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


#########################################################################
# download
#


def download(baseurl, asset_id):
  """
  Downloads the required file from S3 from finding the bucketkey from S3

  Parameters
  ----------
  baseurl: baseurl for web service
  asset_id: User input for asset ID

  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/download'
    url = baseurl + api + '/' + asset_id

    res = requests.get(url)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print(f"Failed with status code: {res.status_code}")
      print(f"url: {url}")
      if res.status_code == 400:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return

    #
    # deserialize and extract asset data:
    #
    body = res.json()
    #
    # let's map each dictionary into a User object:
    #
    image_data = jsons.load(body["data"])
    user_id = jsons.load(body["user_id"])
    asset_name = jsons.load(body["asset_name"])
    bucket_key = jsons.load(body["bucket_key"])

    # To write the output file
    try:
      output_file = open(asset_name, "wb")
      output_file.write(base64.b64decode(body["data"]))
    except Exception as e:
      print("Error writing file: ", e)

    # for row in body["data"]:
    #   asset = jsons.load(row, Asset)
    #   assets_list.append(asset)
    #
    # Now we can think OOP:
    #
    print(f"userid: {user_id}")
    print(f"asset name: {asset_name}")
    print(f"bucket key: {bucket_key}")
    print(f"Downloaded from S3 and saved as \' {asset_name} \'")

  except Exception as e:
    logging.error("download() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


#########################################################################
# download and display
#


def download_and_display(baseurl, asset_id):
  """
  Downloads the required file from S3 from finding the bucketkey from S3 and also display it.

  Parameters
  ----------
  baseurl: baseurl for web service
  asset_id: User input for asset ID

  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/download'
    url = baseurl + api + '/' + asset_id

    res = requests.get(url)

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
    # deserialize and extract asset data:
    #
    body = res.json()
    #
    # let's map each dictionary into a User object:
    #
    image_data = jsons.load(body["data"])
    user_id = jsons.load(body["user_id"])
    asset_name = jsons.load(body["asset_name"])
    bucket_key = jsons.load(body["bucket_key"])

    # To write the output file
    try:
      output_file = open(asset_name, "w")
      output_file.write(base64.b64decode(body["data"]))
    except Exception as e:
      print("Error writing file: ", e)

    # for row in body["data"]:
    #   asset = jsons.load(row, Asset)
    #   assets_list.append(asset)
    #
    # Now we can think OOP:
    #
    print(f"userid: {user_id}")
    print(f"assetname: {asset_name}")
    print(f"bucket key: {bucket_key}")
    print(f"Downloaded from S3 and saved as \' {asset_name} \'")

    # reading the image
    outputImage = img.imread(asset_name)
    # displaying the image
    plt.imshow(outputImage)

  except Exception as e:
    logging.error("download() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


#########################################################################
# bucket
#


def bucket(baseurl):
  """
  Displays information about items in the S3 bucket.

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """
  last_bucket_item = None
  while True:
    try:
      #
      # call the web service:
      #
      api = '/bucket'
      url = baseurl + api
      if last_bucket_item != None:
        url = url + f"?startafter={last_bucket_item.Key}"

      res = requests.get(url)

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
      # deserialize and extract assets:
      #
      body = res.json()
      #
      # let's map each dictionary into an Asset object:
      #
      bucket_list = []
      for row in body["data"]:
        bucket_item = jsons.load(row, BucketItem)
        bucket_list.append(bucket_item)
      #
      # Now we can think OOP:
      #
      for bucket_item in bucket_list:
        print(bucket_item.Key)
        print(" ", bucket_item.LastModified)
        # print(" ", bucket_item.ETag)
        print(" ", bucket_item.Size)
        # print(" ", bucket_item.StorageClass)
        last_bucket_item = bucket_item

      # To get request to move to next page only if there are 12 items
      
      another_page = input("another page? [y/n]\n")
      if another_page != 'y':
        break
      else:
        if len(bucket_list) < 12:
          break
      

    except Exception as e:
      logging.error("bucket() failed:")
      logging.error("url: " + url)
      logging.error(e)
      return


#########################################################################
# main
#
print('** Welcome to PhotoApp v2 **')
print()

# eliminate traceback so we just get error message:
sys.tracebacklimit = 0

#
# what config file should we use for this session?
#
config_file = 'photoapp-client-config.ini'

print("What config file to use for this session?")
print("Press ENTER to use default (photoapp-client-config.ini),")
print("otherwise enter name of config file>")
s = input()

if s == "":  # use default
  pass  # already set
else:
  config_file = s

#
# does config file exist?
#
if not pathlib.Path(config_file).is_file():
  print("**ERROR: config file '", config_file, "' does not exist, exiting")
  sys.exit(0)

#
# setup base URL to web service:
#
configur = ConfigParser()
configur.read(config_file)
baseurl = configur.get('client', 'webservice')

# print(baseurl)

#
# main processing loop:
#
cmd = prompt()

while cmd != 0:
  #
  if cmd == 1:
    stats(baseurl)
  elif cmd == 2:
    users(baseurl)
  elif cmd == 3:
    assets(baseurl)
  elif cmd == 4:
    print("Enter asset id>")
    asset_id = input()
    download(baseurl, asset_id)
  elif cmd == 5:
    print("Enter asset id>")
    asset_id = input()
    download_and_display(baseurl, asset_id)
  elif cmd == 6:
    bucket(baseurl)
  else:
    print("** Unknown command, try again...")
  #
  cmd = prompt()

#
# done
#
print()
print('** done **')
