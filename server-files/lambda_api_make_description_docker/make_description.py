# Importing packages
# from flask import Flask, request, jsonify, Response
from langchain.llms import OpenAI
import openai
from configparser import ConfigParser
import json
import os

def lambda_handler(event, context):
    #Accessing the API Key
    config_file = "config/config.ini"
    configur = ConfigParser()
    configur.read(config_file)
    os.environ["OPENAI_API_KEY"] = configur.get('openai-api', 'api_key')
    print(os.environ["OPENAI_API_KEY"])

    try:
        print("We are inside the lambda.")

        # print(event)

        # if "body" not in event:
        #     return "event has no body"
            # raise Exception("event has no body")
        
        # body = json.loads(event["body"]) # parse the json
        
        # Accessing the incoming data
        bedrooms = event["bedrooms"]
        bathrooms = event["bathrooms"]
        square_feet = event["square_feet"]
        cityname = event["cityname"]
        has_photos = None
        if event["has_photo"] == "Yes": 
            has_photos = "There are display pictures."
        else:
            has_photos = "There are no display pictures."

        dogs_allowed = None
        if event["dogs_allowed"] == "Yes":
            dogs_allowed = "It is dog-friendly."
        else:
            dogs_allowed = "It is not dog-friendly."

        cats_allowed = None
        if event["cats_allowed"] == "Yes":
            cats_allowed = "It is cat-friendly."
        else:
            cats_allowed = "It is not cat-friendly."
        
        amenities = "The amenities available are " + ", ".join(event["amenities"]) + "."

        print(bedrooms)
        print(bathrooms)
        print(square_feet)
        print(cityname)
        print(has_photos)
        print(dogs_allowed)
        print(cats_allowed)
        print(amenities)
    except Exception as err:
        print("An error has occured while generating the response.")
        print(err)
        # return err
        return {
            'statusCode': 400,
            'description': err
        }

    # Create the prompt for LLM
    prompt = f"There is a house with {bedrooms} bedrooms, {bathrooms} bathrooms with an area of {square_feet} sq. feet. It is located in {cityname}. {dogs_allowed} {cats_allowed} {has_photos}. {amenities} Make a description for a rental posting on Zillow."
    model = "gpt-3.5-turbo"
    num_tokens = 100
    print(prompt)
    try:
        # Define LLM Model
        llm = OpenAI(temperature=0)
        # Generate response
        response = llm(prompt)
        print(response)
        return {
            'statusCode': 200,
            'description': response
        }
    except Exception as err:
        print(err)
        return {
            'statusCode': 400,
            'description': err
        }
