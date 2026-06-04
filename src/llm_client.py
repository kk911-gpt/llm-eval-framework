"""
llm_client.py
─────────────
Handles all communication with the LLM (Llama 3.3 70B via Groq).
Every other file uses get_response() to talk to the AI.
"""

import os
from groq import Groq
from config import GROQ_API_KEY, MODEL_NAME

# Create one single connection to Groq
# This connection is reused for every prompt
client = Groq(api_key=GROQ_API_KEY)


def get_response(prompt: str) -> str:
    """
    Send a prompt to the LLM and return its response.
    
    Args:
        prompt: The question or instruction to send
        
    Returns:
        The LLM's response as a string
        
    Example:
        response = get_response("Who walked on the moon first?")
        # returns "Neil Armstrong walked on the moon in 1969"
    """
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    
    except Exception as e:
        # If API call fails, return error message instead of crashing
        return f"ERROR: {str(e)}"