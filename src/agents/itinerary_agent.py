from utils.api_utils import call_llm
import json

def generate_itinerary(user):
    destination = user["destination"]
    duration = user["duration"]
    travelers = user["travelers"]
    budget = user["budget"]

    prompt = f"""
You are ItineraryAgent. Generate a JSON itinerary for:
Destination: {destination}
Duration: {duration} days
Budget: {budget} INR
Travelers: {travelers}

Return STRICT JSON with keys:
- per_day_breakdown (list)
- accommodation
- transport
- top_places
- summary
- total_budget

DO NOT add comments, only valid JSON.
"""

    raw = call_llm(prompt)
    try:
        return json.loads(raw)
    except:
        return {"error": "invalid_json", "raw": raw}
