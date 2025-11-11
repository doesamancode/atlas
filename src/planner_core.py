from utils.api_utils import call_llm
import json

def generate_plan(destination, budget, travelers, duration):
    prompt = f"""
You are a professional genius travel-planning assistant. Output a JSON object ONLY (no extra text) with these keys:
- destination (string)
- duration (int)
- total_budget (string or number)
- travelers (int)
- per_day_breakdown (array of objects) each with: day (int), title (string), activities (array of strings), estimated_cost (string/number)
- accommodation (object) with type, example, estimated_cost
- transport (object) with recommended_transport and estimated_cost
- top_places (array of strings)
- summary (string)

Destination: {destination}
Budget: {budget}
Travelers: {travelers}
Duration: {duration}

Ensure JSON is valid. Numbers as numbers. Do not include any backticks or markdown.
"""
    raw = call_llm(prompt)
    # attempt to parse
    try:
        parsed = json.loads(raw)
        return parsed
    except json.JSONDecodeError:
        # fallback: try to extract JSON substring
        import re
        m = re.search(r'(\{.*\})', raw, re.S)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                pass
        return {"error": "could not parse JSON from model", "raw": raw}
