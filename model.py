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
from room_agent import RoomSearchAgent
from flight_agent import FlightSearchAgent
import requests


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
