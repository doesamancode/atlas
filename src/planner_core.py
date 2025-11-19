from orchestrator import run_agentic_pipeline

def generate_plan(destination, budget, travelers, duration):
    user_input = {
        "destination": destination,
        "budget": budget,
        "travelers": travelers,
        "duration": duration
    }

    plan = run_agentic_pipeline(user_input)
    return plan
