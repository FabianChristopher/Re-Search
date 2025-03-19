import os
from config import get_openai_api_key

# Set OpenAI API key as an environment variable
os.environ["OPENAI_API_KEY"] = get_openai_api_key()

import openai
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI()

def extract_main_keyword(text):
    """
    Extracts the main topic keyword from the given text using OpenAI's GPT-4 API.
    Returns only one keyword (e.g., "Deep Learning", "Natural Language Processing").
    """
    prompt = (
        "Extract the **main topic keyword** from the following text. "
        "Return **only one** keyword that best represents the entire content. "
        "Do **not** return full sentences, explanations, or extra text. "
        "Only return a **single** keyword or short phrase like "
        "'Deep Learning', 'Natural Language Processing', 'Quantum Computing', etc."
        "The Keyword must NOT be an abbreviation or a shortened term like NLP or ML or AI. It should be expanded into its full form like Natural language Processing or Machine learning \n\n"
        f"Text:\n{text}\n\n"
        "Main Topic Keyword:"
    )
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        keyword = completion.choices[0].message.content.strip()
    except Exception as e:
        keyword = f"Error extracting keyword: {str(e)}"
    
    return keyword
