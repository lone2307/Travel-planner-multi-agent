import getpass
import os
from dotenv import load_dotenv, set_key

env_path = ".env"

load_dotenv(env_path)

def _set_if_undefined(var: str):
    if not os.environ.get(var):
        set_key(env_path, var, getpass.getpass(f"Please provide your {var}"))


_set_if_undefined("GOOGLE_API_KEY")
_set_if_undefined("TAVILY_API_KEY")