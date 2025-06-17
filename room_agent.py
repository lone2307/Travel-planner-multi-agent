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
    def __init__(self, model, verbose):
        self.model = model
        self.verbose = verbose

    def generate(self):
        @tool
        def get_room_price(location: str, checkin: str,checkout: str,  people: int) -> str:
            """Get the price of the surrounding hotels given the location, check-in, check-out date and number of people
            checkin is the check-in date, format year-month-date (eg. 2025-07-06)
            checkout is the check-out date, format the same as checkin

            """

        promt = (
            "You are a research agent.\n\n"
            "INSTRUCTIONS:\n"
            "- Assist ONLY with finding the cheapest flight from A to B during the time frame with the cheapest price tag\n"
            "- After you're done with your tasks, respond to the supervisor directly\n"
            "- Respond ONLY with the results of your work, do NOT include ANY other text.\n"
        )

        room_agent = create_react_agent(
            model = self.model,
            tools = [get_room_price],
            prompt = promt,
            name = "research_agent"
        )
        return room_agent