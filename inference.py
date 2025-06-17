from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from model import get_hotel_detail



get_hotel_detail("g293916-d19626625", "2025-06-19", "2025-06-20", 1)