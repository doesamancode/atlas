# agents/validation_agent.py

def infer_trip_region(destinations):
    """
    Very simple heuristic to classify trip type based on destination names.
    If any destination matches long-haul keywords → long_haul
    Else if any matches Asia/Middle-East → asia
    Else → domestic (India assumed as base)
    """
    if not destinations:
        return "domestic"

    long_haul_keywords = {
        # Countries / regions
        "canada", "usa", "united states", "america", "uk", "england", "britain",
        "london", "france", "paris", "germany", "berlin", "italy", "rome",
        "spain", "madrid", "barcelona", "switzerland", "zurich", "geneva",
        "netherlands", "amsterdam", "belgium", "australia", "sydney", "melbourne",
        "new zealand", "auckland", "toronto", "vancouver", "los angeles",
        "new york", "san francisco", "boston", "chicago", "mauritius"
    }

    asia_keywords = {
        "singapore", "thailand", "bangkok", "phuket", "krabi",
        "malaysia", "kuala lumpur", "indonesia", "bali",
        "vietnam", "hanoi", "ho chi minh",
        "sri lanka", "colombo",
        "nepal", "kathmandu",
        "bhutan",
        "maldives",
        "qatar", "doha",
        "dubai", "uae", "abu dhabi",
        "hong kong", "japan", "tokyo", "osaka",
        "china", "beijing", "shanghai"
    }

    # First pass: long-haul detection
    for dest in destinations:
        d = dest.lower()
        if any(kw in d for kw in long_haul_keywords):
            return "long_haul"

    # Second pass: Asia / nearby
    for dest in destinations:
        d = dest.lower()
        if any(kw in d for kw in asia_keywords):
            return "asia"

    # Fallback: assume domestic (India)
    return "domestic"


def validate(plan, user_input):
    errors = []

    budget = user_input.get("budget", 0) or 0
    travelers = user_input.get("travelers", 1) or 1
    duration = user_input.get("duration", 1) or 1
    destinations = user_input.get("destinations", []) or []

    # ---- Basic numeric sanity ----
    if budget <= 0 or duration <= 0 or travelers <= 0:
        errors.append("Invalid numeric inputs (budget, duration, or travelers).")

    # ---- City/day feasibility ----
    if len(destinations) > duration:
        errors.append("Too many destinations for the given number of days.")

    # ---- Budget realism by region ----
    trip_type = infer_trip_region(destinations)

    per_day_min = {
        "domestic": 1500,
        "asia": 6000,
        "long_haul": 15000,
    }.get(trip_type, 1500)

    required_min = per_day_min * duration * travelers

    if budget < required_min:
        errors.append(
            f"Budget too low for a {trip_type.replace('_', ' ')} trip. "
            f"Minimum expected: ₹{required_min:,} for {duration} day(s) × {travelers} traveler(s)."
        )

    # ---- Structural checks on the plan ----
    if not plan.get("city_accommodations"):
        errors.append("Missing per-city accommodation details.")

    per_day = plan.get("per_day_breakdown", [])
    if not isinstance(per_day, list):
        errors.append("Invalid per-day breakdown structure.")
    else:
        for day in per_day:
            day_num = day.get("day", "?")
            if not day.get("activities"):
                errors.append(f"Day {day_num} has no activities listed.")
            est = day.get("estimated_cost", 0)
            if est is None or est < 0:
                errors.append(f"Day {day_num} has invalid estimated cost.")

    # ---- Final verdict ----
    return (len(errors) == 0, errors)
