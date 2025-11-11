import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Fetch Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("⚠️ GEMINI_API_KEY not found in .env file")

genai.configure(api_key=GEMINI_API_KEY)

# Example config values
PROJECT_NAME = "Agentic Travel Planner"
VERSION = "0.1"
DEFAULT_MODEL = "gemini-2.5-flash"
