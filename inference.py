from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from food_agent import get_location


get_location(21.0278, 105.8342)