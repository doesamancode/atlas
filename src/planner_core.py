from orchestrator import run_agentic_pipeline

def generate_plan(payload):
    """
    Agentic planner entrypoint.
    Accepts ONE dict payload from the Streamlit app.

    Expected payload structure:
    {
        "source": str,
        "destinations": [str, str, ...],
        "budget": int,
        "travelers": int,
        "duration": int
    }
    """

    source = payload.get("source")
    destinations = payload.get("destinations", [])
    budget = payload.get("budget")
    travelers = payload.get("travelers")
    duration = payload.get("duration")

    # ensure destinations is a list
    if isinstance(destinations, str):
        destinations = [d.strip() for d in destinations.split(",") if d.strip()]

    # Pass UNPACKED values to orchestrator
    plan = run_agentic_pipeline(source, destinations, duration, budget, travelers)

    return plan
