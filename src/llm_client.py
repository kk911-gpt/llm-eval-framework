import os
from groq import Groq
from config import GROQ_API_KEY, MODEL_NAME

# This file handles all communication with the AI
client = Groq(api_key=GROQ_API_KEY)

def get_response(prompt: str) -> str:
    """Send a prompt to the AI and get a response back"""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"ERROR: {str(e)}"