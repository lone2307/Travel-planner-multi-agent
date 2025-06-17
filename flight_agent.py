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


web_search = TavilySearch(
    max_result = 5,
    topic = "general",
    search_depth = "advanced",
    include_raw_content="text"
)

class FlightSearchAgent:
    def __init__(self, model):
        self.model = model
    
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
