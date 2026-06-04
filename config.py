import os
from dotenv import load_dotenv

load_dotenv()

# Groq settings
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama-3.3-70b-versatile"

# LangSmith settings
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT")

# Eval settings
TOTAL_PROMPTS = 100
FAILURE_THRESHOLD = 0.5