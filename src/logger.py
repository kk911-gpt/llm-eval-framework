import os
from datetime import datetime
from langsmith import Client
from config import LANGCHAIN_API_KEY, LANGCHAIN_PROJECT

# This file handles all logging to LangSmith
os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY or ""
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT or "llm-eval-framework"

def log_result(prompt: str, response: str, category: str, score: float, passed: bool):
    """Log a single eval result"""
    result = {
        "timestamp": datetime.now().isoformat(),
        "category": category,
        "prompt": prompt,
        "response": response,
        "score": score,
        "passed": passed
    }
    print(f"[{category}] Score: {score:.2f} | {'PASS' if passed else 'FAIL'}")
    return result