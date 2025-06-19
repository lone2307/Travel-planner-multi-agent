from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_tavily import TavilySearch
import requests


web_search_minimal = TavilySearch(
    max_result = 1,
    topic = "general",
)


def get_hotel_list(location):
    location_url  = web_search_minimal.invoke(f"tripadvisor hotel in {location}")["results"][0]["url"]
    location_code = location_url[...,location_url[location_url.index('g'),...].index("-")]

    url = f"https://data.xotelo.com/api/list?location_key={location_code}&limit=5"
    hotel_list = requests.get(url).json()
    hotel_list = hotel_list["results"]["list"]
    hotel_sorted = sorted(hotel_list, key=lambda i: i["price_ranges"]["maximum"])
    
    return hotel_sorted

def get_hotel_detail(hotel_id, check_in, check_out, people):
    url = f"https://data.xotelo.com/api/rates?hotel_key={hotel_id}&chk_in={check_in}&chk_out={check_out}&adults={people}"
    get_rate = requests.get(url).json()["result"]["rates"][0]
    return get_rate


class RoomSearchAgent:
    def __init__(self, model):
        self.model = model

    def generate(self):
        @tool
        def get_room_price(location: str, checkin: str,checkout: str,  people: int) -> str:
            """Get the price of the surrounding hotels given the location, check-in, check-out date and number of people
            checkin is the check-in date, format year-month-date (eg. 2025-07-06)
            checkout is the check-out date, format the same as checkin
            return the rate for 1 night for the hotel
            """

            hotel_list = get_hotel_list(location)
        
        @tool
        def cost_counter(rate: float, nights: int) -> str:
            """Get the cost hotel for the whole trip
            input: rate (float): the cost for 1 night, nights (int): the number of nights stay at the hotel
            output: the cost for hotel for the whole trip
            """

            return rate * nights

        promt = (
            "You are a research agent.\n\n"
            "INSTRUCTIONS:\n"
            "- Assist ONLY with finding the cheapest hotel during the stay\n"
            "- ONLY return 1 hotel, including the total price and the name of hotel\n"
            "- After you're done with your tasks, respond to the supervisor directly\n"
            "- Respond ONLY with the results of your work, do NOT include ANY other text.\n"
        )

        room_agent = create_react_agent(
            model = self.model,
            tools = [get_room_price, cost_counter],
            prompt = promt,
            name = "research_agent"
        )
        return room_agent