from src.utils.api_utils import call_llm

def generate_plan(destination, budget, travelers, duration):
    prompt = f"""
    You are a smart, detail-oriented travel assistant.
    Create a {duration}-day travel itinerary for {travelers} travelers visiting {destination}
    with a total budget of {budget}.
    Include daily activities, food suggestions, accommodation type, and approximate costs.
    Output in a clean, readable format.
    """
    return call_llm(prompt)
