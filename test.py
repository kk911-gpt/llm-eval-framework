import os
from dotenv import load_dotenv
from groq import Groq

# Load your API keys from .env file
load_dotenv()

# Connect to Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Send a simple prompt to the AI
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", "content": "Say hello in one sentence."}
    ]
)

# Print the response
print("AI Response:", response.choices[0].message.content)
print("Connection successful!")