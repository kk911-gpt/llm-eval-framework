"""
config.py
─────────
Central configuration file for the entire project.
All settings live here so you only need to change one place.
"""

import os
from dotenv import load_dotenv

# Load API keys from .env file into memory
load_dotenv()

# ─────────────────────────────────────────
# LLM SETTINGS
# ─────────────────────────────────────────
# Your Groq API key (loaded from .env file)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Which AI model to use for both student and judge
MODEL_NAME = "llama-3.3-70b-versatile"

# ─────────────────────────────────────────
# LANGSMITH SETTINGS
# ─────────────────────────────────────────
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT")

# ─────────────────────────────────────────
# EVALUATION SETTINGS
# ─────────────────────────────────────────
# Total number of prompts to test per run
TOTAL_PROMPTS = 100

# Score threshold — below this = FAIL, above this = PASS
FAILURE_THRESHOLD = 0.5