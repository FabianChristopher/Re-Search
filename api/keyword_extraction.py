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
        "You are an expert at understanding academic search queries and generating powerful multi-keyword research phrases.\n\n"
        "Given a user’s text, extract a **5–6 word search phrase** containing the most important and relevant keywords. "
        "You must understand the user’s intent and choose keywords that help retrieve the most useful academic papers.\n\n"
        "**Rules:**\n"
        "- Focus on the core *topics or problems* the user is interested in.\n"
        "- Do **not** include abbreviations like NLP or ML — expand them.\n"
        "- If the user says 'don't include X', completely avoid it.\n"
        "- Use 5–6 descriptive words that capture the user’s intent.\n"
        "- Do not include filler words or punctuation.\n"
        "- Output must be a single line containing just the search phrase — no extra text.\n\n"
        "**Examples:**\n"
        "User: I want to study the ethics of generative AI but not NLP.\n"
        "→ generative artificial intelligence ethics fairness\n\n"
        "User: Find papers on robotic surgery and computer vision.\n"
        "→ robotic surgery computer vision systems\n\n"
        f"User: {text}\n"
        "→"
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
