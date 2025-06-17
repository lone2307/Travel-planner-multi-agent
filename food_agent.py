from langgraph.prebuilt import create_react_agent
from langchain_tavily import TavilySearch
from langchain_core.tools import tool

search_engine = TavilySearch(
    max_result = 5,
    topic = "general",
    search_depth = "advanced",
    include_raw_content="text"
)




class FoodResearchAgent:
    def __init__(self, model):
        self.model = model

    def generate(self):
        @tool
        def food_search(location: str) -> str:
            return


        agent = create_react_agent(
            model = self.model,
            tools = [],
            prompt= (),
        )