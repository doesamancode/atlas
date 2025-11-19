from utils.api_utils import call_llm
import json, re

def repair_json(output):
    """
    Extract & repair malformed JSON using regex.
    """
    match = re.search(r"\{[\s\S]*\}", output)
    if match:
        try:
            return json.loads(match.group(0))
        except:
            pass
    return {"error": "invalid_json", "raw": output}


def generate_itinerary(user):
    """
    Generate a multi-city itinerary with:
    - per-city day allocation
    - per-city accommodation recommendations
    - strict JSON output
    """
    source = user.get("source", "")
    destinations = user.get("destinations", [])
    duration = int(user.get("duration", 1))
    budget = user.get("budget", 0)
    travelers = user.get("travelers", 1)

    if not destinations:
        destinations = ["Unknown City"]

    # Day Allocation
    n = len(destinations)
    base = duration // n
    extra = duration % n

    allocation = []
    for i, city in enumerate(destinations):
        days = base + (1 if i < extra else 0)
        allocation.append((city, days))

    alloc_text = "\n".join([f"- {city}: {d} day(s)" for city, d in allocation])
    dest_display = ", ".join(destinations)

    # ULTRA PRO PROMPT — per-city accommodations
    prompt = f"""
You are ATLAS, a professional multi-destination travel planner AI.

Generate an itinerary ONLY in valid JSON using this EXACT structure:

{{
  "destination": "{source} → {dest_display}",
  "duration": {duration},
  "total_budget": {budget},
  "travelers": {travelers},

  "per_day_breakdown": [
    {{
      "day": 1,
      "city": "City Name",
      "title": "Short title for the day",
      "activities": ["Activity 1", "Activity 2"],
      "estimated_cost": 0
    }}
  ],

  "city_accommodations": [
    {{
      "city": "City Name",
      "hotel": "Hotel Name (not chain of multiple hotels)",
      "type": "Hotel/Hostel Category",
      "estimated_cost": 0
    }}
  ],

  "accommodation": {{
    "type": "General accommodation category",
    "example": "Overall example stay",
    "estimated_cost": 0
  }},

  "transport": {{
    "recommended_transport": "",
    "estimated_cost": 0
  }},

  "top_places": ["Place 1", "Place 2"],
  "summary": "Short summary paragraph."
}}

IMPORTANT RULES:
- DO NOT mix hotels. ONE hotel per city.
- If a hotel name includes parentheses, ensure they do NOT contain another city.
- For each destination in this exact list: {dest_display}, generate EXACTLY one hotel.
- Distribute days exactly as follows:
{alloc_text}

RETURN ONLY JSON. NO markdown. NO commentary.
"""

    raw = call_llm(prompt)

    # Try direct JSON parsing
    try:
        return json.loads(raw)
    except:
        return repair_json(raw)
