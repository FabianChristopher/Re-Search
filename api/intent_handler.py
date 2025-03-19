import openai
from config import get_openai_api_key
from openai import OpenAIError

# Define system prompt for intent detection
INTENT_PROMPT = """
You are an AI assistant that classifies user queries into predefined intents.

User queries are related to research papers. Your task is to:
1. Identify all valid intents from the list below.
2. Return the intents in the correct execution order.

Valid intents:
- search_papers: When the user asks to find papers on a topic.
- recommend_papers: When the user asks for similar papers.
- lookup_citations: When the user asks for citation details of a paper.
- summarize_paper: When the user asks for a summary of a paper.
- fetch_authors: When the user asks for the authors of a paper.
- fetch_pdf: When the user asks for the full-text PDF of a paper.
- compare_papers: When the user asks to compare two papers.

⚠️ Rules:
- If the user query is casual conversation, return "no_intent".
- Do NOT force intents if they are not in the user's request.
- If multiple intents exist, return them in the correct order.
- Return only the intent names exactly as listed above.

Example:
User: "Find papers on NLP and summarize the best one."
Response: "search_papers, summarize_paper"

User: "What do you think of transformers in NLP?"
Response: "no_intent"
"""

def detect_intent(user_message):
    """Uses OpenAI API to detect user intent from the input message."""
    api_key = get_openai_api_key()
    client = openai.Client(api_key=api_key)  # Use OpenAI Client

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": INTENT_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0
        )

        detected_intents = response.choices[0].message.content.strip()
        return detected_intents

    except OpenAIError as e:
        return f"Error: {str(e)}"
