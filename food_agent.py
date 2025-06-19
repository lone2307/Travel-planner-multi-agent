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

def get_coordinates(address):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': address,
        'key': GOOGLE_PLACE_API
    }
    response = requests.get(base_url, params=params)
    data = response.json()

    if data['status'] == 'OK':
        latitude = data['results'][0]['geometry']['location']['lat']
        longitude = data['results'][0]['geometry']['location']['lng']
        return latitude, longitude
    else:
        print(f"Error: {data['status']}")
    return None, None

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

    return requests.post(url, headers=header, json=data).json()



class FoodResearchAgent:
    def __init__(self, model):
        self.model = model

    def generate(self):
        @tool
        def food_search(location: float) -> str:
            """Get the top 5 restaurants when giving the relative location in format of string (eg. Eiffel Tower, Paris)
            Return the types of restaurant, name of restaurant and formatted address of the restaurant
            """
            lat, lon = get_coordinates(location)
            return get_location(lat,lon)
        

        prompt = (
            "You are a research agent.\n\n"
            "INSTRUCTIONS:\n"
            "- Assist ONLY with finding the top 5 restaurants given the location of the place\n"
            "- Format each restaurant like this: [name], [3 restaurant tags], [location] \n"
            "- After you're done with your tasks, respond to the supervisor directly\n"
            "- Respond ONLY with the results of your work.\n"
        )

        agent = create_react_agent(
            model  = self.model,
            tools  = [food_search],
            prompt = prompt,
        )