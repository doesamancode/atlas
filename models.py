import google.generativeai as genai
from src.config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

models = genai.list_models()
for m in models:
    print(m.name, "-", m.supported_generation_methods)
