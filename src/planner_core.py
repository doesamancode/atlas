from orchestrator import run_agentic_pipeline

def generate_plan(source, destinations, budget, travelers, duration):
    """
    Agentic planner entrypoint.
    source: starting city (string)
    destinations: list of destination city names
    budget: total budget (number)
    travelers: number of travelers (int)
    duration: total trip days (int)
    """

    # ensure destinations is a list
    if isinstance(destinations, str):
        destinations = [destinations]

    user_input = {
        "source": source,
        "destinations": destinations,
        "budget": budget,
        "travelers": travelers,
        "duration": duration
    }

    plan = run_agentic_pipeline(user_input)
    return plan
