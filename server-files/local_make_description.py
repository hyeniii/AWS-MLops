# Importing packages
from flask import Flask, request, jsonify, Response
from langchain.llms import OpenAI
from configparser import ConfigParser
import os

#Accessing the API Key
config_file = "config/config.ini"
configur = ConfigParser()
configur.read(config_file)
os.environ["OPENAI_API_KEY"] = configur.get('openai-api', 'api_key')

# Create Flask Instance
app = Flask(__name__)

# Define API endpoint and request method
@app.route("/make_description", methods = ["PUT"])
def make_description():
    try:
        # Get the data from the incoming request
        incoming_data = request.get_json()
        print(incoming_data)
        # col_names = list(incoming_data.keys())
        # data = {col: data[0][col] for col in col_names}

        # Extracting each aspect of the data
        bedrooms = incoming_data["bedrooms"]
        bathrooms = incoming_data["bathrooms"]
        square_feet = incoming_data["square_feet"]
        cityname = incoming_data["cityname"]
        has_photos = None
        if incoming_data["has_photos"] == "Yes":
            has_photos = "There are display pictures."
        else:
            has_photos = "There are no display pictures."

        pets_allowed = None
        if incoming_data["pets_allowed"] == "Yes":
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
        return jsonify({'status': 400, 'description': err})

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
        return jsonify({'status': 200, 'description': response})
    except Exception as err:
        return jsonify({'status': 400, 'description': err})

# Run the Flask app
app.run(host='0.0.0.0', port=2000)
