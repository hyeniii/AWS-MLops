from langchain.llms import OpenAI
import os

os.environ["OPENAI_API_KEY"] = "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"

def make_description():
    bedrooms = 5
    bathrooms = 4
    square_feet = 3000
    cityname = "Chicago"
    has_photos = "There are display pictures."
    pets_allowed = "It is pet-friendly."
    
    # Create the prompt for LLM
    prompt = f"There is a house with {bedrooms} bedrooms, {bathrooms} bathrooms with an area of {square_feet} sq. feet. It is located in {cityname}. {pets_allowed} {has_photos} Make a description for a rental posting on Zillow."
    model = "gpt-3.5-turbo"
    num_tokens = 100
    print(prompt)

    # Define LLM Model
    llm = OpenAI(temperature=0)

    # Generate response
    response = llm(prompt)
    print(response)

make_description()