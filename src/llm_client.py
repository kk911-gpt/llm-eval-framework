import time
from groq import Groq
from config import GROQ_API_KEY, MODEL_NAME

client = Groq(api_key=GROQ_API_KEY)

def get_response(prompt: str, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            time.sleep(2)  # small delay between calls
            return response.choices[0].message.content

        except Exception as e:
            error_msg = str(e)

            if "Connection" in error_msg or "connect" in error_msg.lower():
                if attempt < retries - 1:
                    wait_time = (attempt + 1) * 5
                    print(f"\n  Connection error. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue

            if "429" in error_msg or "rate_limit" in error_msg.lower():
                wait_time = 10
                print(f"\n  Rate limit hit. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue

            return f"ERROR: {error_msg}"

    return "ERROR: Max retries exceeded"