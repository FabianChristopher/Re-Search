import os
import random
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Store API keys in a list
OPENAI_API_KEYS = list(filter(None, [os.getenv("OPENAI_API_KEY_1"), os.getenv("OPENAI_API_KEY_2")]))

def get_openai_api_key():
    """Returns a random OpenAI API key to distribute requests."""
    if not OPENAI_API_KEYS:
        raise ValueError("No OpenAI API keys found in the environment variables.")
    return random.choice(OPENAI_API_KEYS)
