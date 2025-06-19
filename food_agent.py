from dotenv import load_dotenv
import os
from langgraph.prebuilt import create_react_agent
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
import requests
import json

load_dotenv('.env')
GOOGLE_PLACE_API = os.getenv('GOOGLE_PLACE_API')




search_engine = TavilySearch(
    max_result = 5,
    topic = "general",
    search_depth = "advanced",
    include_raw_content="text"
)

def get_location(LATITUDE, LONGITUDE):
    url = "https://places.googleapis.com/v1/places:searchNearby"
    header = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_PLACE_API,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.types" 
    }
    data = {
        "includedTypes": ["restaurant"],
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": LATITUDE,
                    "longitude": LONGITUDE
                },
                "radius": 10000
            }
        },
        "maxResultCount": 5
    }

    POST_get = requests.post(url, headers=header, json=data).json()
    print(POST_get)


class FoodResearchAgent:
    def __init__(self, model):
        self.model = model

    def generate(self):
        @tool
        def get_lat_long(location: str) -> str:
            """Get the LATITUDE and LONGITUDE given the name of the location.
            Search though the text to find the coordinates, format it in 
            """

        @tool
        def food_search(latitude: int, longitude: int) -> str:
            """Get the top 5 restaurants given the latitude and longitude in format of integer (eg. 21.0278, 105.8342)
            Return the types of restaurant, name of restaurant and formatted address of the restaurant
            """
            return
        

        prompt = (
            "You are a research agent.\n\n"
            "INSTRUCTIONS:\n"
            "- Assist ONLY with finding the top 5 restaurants given the location of the place\n"
            "- \n"
            "- After you're done with your tasks, respond to the supervisor directly\n"
            "- Respond ONLY with the results of your work.\n"
        )


        agent = create_react_agent(
            model  = self.model,
            tools  = [get_lat_long, food_search],
            prompt = prompt,
        )