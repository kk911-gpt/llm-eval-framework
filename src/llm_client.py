"""
llm_client.py
─────────────
Handles all communication with the LLM.
Includes automatic retry logic for connection errors.
"""

import time
from groq import Groq
from config import GROQ_API_KEY, MODEL_NAME

client = Groq(api_key=GROQ_API_KEY)


def get_response(prompt: str, retries: int = 3) -> str:
    """
    Send a prompt to the LLM and return its response.
    Automatically retries up to 3 times on connection errors.
    """
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content

        except Exception as e:
            error_msg = str(e)
            
            # Connection error — wait and retry
            if "Connection" in error_msg or "connect" in error_msg.lower():
                if attempt < retries - 1:
                    wait_time = (attempt + 1) * 5
                    print(f"\n  ⚠️ Connection error. Retrying in {wait_time}s... (attempt {attempt + 1}/{retries})")
                    time.sleep(wait_time)
                    continue
            
            # Rate limit — wait longer
            if "429" in error_msg or "rate_limit" in error_msg.lower():
                print(f"\n  ⚠️ Rate limit hit. Waiting 60 seconds...")
                time.sleep(60)
                continue
            
            return f"ERROR: {error_msg}"
    
    return "ERROR: Max retries exceeded"