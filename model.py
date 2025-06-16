import os
from urllib import response
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain.memory import ConversationBufferWindowMemory
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from langchain_tavily import TavilySearch
import requests



web_search = TavilySearch(
    max_result = 5,
    topic = "general",
    search_depth = "advanced",
    include_raw_content="text"
)

web_search_minimal = TavilySearch(
    max_result = 1,
    topic = "general",
)


def get_hotel_list(location):
    location_url  = web_search_minimal.invoke(f"tripadvisor hotel in {location}")["results"][0]["url"]
    location_code = location_url[...,location_url[location_url.index('g'),...].index("-")]

    url = f"https://data.xotelo.com/api/list?location_key={location_code}&limit=5"
    hotel_list = requests(url).json()
    hotel_list = hotel_list["results"]["list"]
    hotel_sorted = sorted(hotel_list, key=lambda i: i["price_ranges"]["maximum"])
    
    return hotel_sorted

def get_hotel_detail(hotel_id, check_in, check_out, adult, children):
    url = f"https://data.xotelo.com/api/rates?hotel_key={hotel_id}&check_in_date={check_in}&check_out_date={check_out}"



class FlightSearchAgent:
    def __init__(self, model, verbose):
        self.model = model
        self.verbose = verbose
    
    def generate(self):
        @tool 
        def get_flight_result(A: str, B: str, time_duration: str) -> str:
            """Get the price for a round trip flight from A to B during the time frame.
            A, B are name of locations (eg. Hanoi, London)
            time_duration is the time of the trip (eg. 26 Jun 2025 to 28 Jun 2025)
            """

            response = web_search.invoke(f"round trip flight from {A} to {B} from {time_duration}")
            return response["results"][...]["content"]

        promt = (
            "You are a research agent.\n\n"
            "INSTRUCTIONS:\n"
            "- Assist ONLY with finding the cheapest flight from A to B during the time frame with the cheapest price tag\n"
            "- After you're done with your tasks, respond to the supervisor directly\n"
            "- Respond ONLY with the results of your work, do NOT include ANY other text.\n"
        )

        flight_agent = create_react_agent(
            model = self.model,
            tools = [get_flight_result],
            prompt = promt,
            name = "research_agent"
        )
        return flight_agent

class RoomSearchAgent:
    def __init__(self, model, verbose):
        self.model = model
        self.verbose = verbose

    def generate(self):
        @tool
        def get_room_price(location: str, time_duration: str, people: int) -> str:
            """Get the price of the surrounding hotels given the location, number of people and time duration
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
            tools = [],
            prompt = promt,
            name = "research_agent"
        )
        return room_agent


class MultiAgentSystem:
    def __init__(self, model, verbose):
        self.model = model
        self.verbose = verbose

        self.flight_agent = FlightSearchAgent(model, verbose)
        self.room_agent   = RoomSearchAgent(model, verbose)

    
    def generate(self):
        text = ""


        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful AI assistant specialized in providing current weather and future forecasts. Always use the available tools to get accurate information. If a user asks for a forecast, try to get the forecast for tomorrow (1 day out) unless specified otherwise."),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        memory = ConversationBufferWindowMemory(
            k=5,
            memory_key="chat_history",
            return_messages=True
        )

        orchestrator = create_supervisor(
            model = self.model,
        )

        executor = AgentExecutor(
            agent=orchestrator,
            memory=memory,
            verbose=self.verbose,
        )
        return text
