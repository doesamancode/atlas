from agents.itinerary_agent import generate_itinerary
from agents.budget_agent import optimize_budget, calculate_total
from agents.validation_agent import validate
from agents.feedback_agent import refine_state

def run_agentic_pipeline(user_input, max_loops=3):
    state = {"user": user_input, "plan": {}}

    for _ in range(max_loops):

        # --- Itinerary Agent ---
        itinerary = generate_itinerary(user_input)
        if "error" in itinerary:
            return {"error": "invalid_model_output"}

        state["plan"] = itinerary

        # --- Budget Agent ---
        state["plan"] = optimize_budget(state["plan"], user_input["budget"])

        # --- Validation Agent ---
        valid, errors = validate(state["plan"], user_input)
        if valid:
            return state["plan"]

        # if over budget AND total cost is extremely low → impossible case
        total = calculate_total(state["plan"])
        if total < user_input["budget"] * 0.1:   # threshold
            return {"error": "impossible_constraints"}

        # --- Feedback Agent ---
        state = refine_state(state, errors)

    # After max loops, still invalid → inform UI
    return {"error": "constraints_not_met"}
