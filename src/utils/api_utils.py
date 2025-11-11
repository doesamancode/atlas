import google.generativeai as genai
from config import DEFAULT_MODEL
import json

def call_llm(prompt):
    model = genai.GenerativeModel(DEFAULT_MODEL)
    response = model.generate_content(prompt)
    return response.text.strip()