# Importing packages
# from flask import Flask, request, jsonify, Response
from langchain.llms import OpenAI
import openai
from configparser import ConfigParser
import os

def lambda_handler(event, context):
    #Accessing the API Key
    config_file = "config/config.ini"
    configur = ConfigParser()
    configur.read(config_file)
    os.environ["OPENAI_API_KEY"] = configur.get('openai-api', 'api_key')
    print(os.environ["OPENAI_API_KEY"])

    try:
        # Accessing the incoming data
        bedrooms = event["bedrooms"]
        bathrooms = event["bathrooms"]
        square_feet = event["square_feet"]
        cityname = event["cityname"]
        has_photos = None
        if event["has_photos"] == "Yes":
            has_photos = "There are display pictures."
        else:
            has_photos = "There are no display pictures."

        pets_allowed = None
        if event["pets_allowed"] == "Yes":
            pets_allowed = "It is pet-friendly."
        else:
            pets_allowed = "It is not pet-friendly."

        print(bedrooms)
        print(bathrooms)
        print(square_feet)
        print(cityname)
        print(has_photos)
        print(pets_allowed)
    except Exception as err:
        print("An error has occured while generating the response.")
        print(err)
        return {
            'statusCode': 400,
            'description': err
        }

    # Create the prompt for LLM
    prompt = f"There is a house with {bedrooms} bedrooms, {bathrooms} bathrooms with an area of {square_feet} sq. feet. It is located in {cityname}. {pets_allowed} {has_photos}. Make a description for a rental posting on Zillow."
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
