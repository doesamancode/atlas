from agents.itinerary_agent import generate_itinerary
from agents.budget_agent import optimize_budget, calculate_total
from agents.validation_agent import validate
from agents.feedback_agent import refine_state

def run_agentic_pipeline(user_input, max_loops=2):
    """
    Agentic pipeline for ATLAS:
    1) ItineraryAgent → structured base itinerary
    2) BudgetAgent → soft optimization
    3) ValidationAgent → checks structure & costs
    4) FeedbackAgent → refines (if needed)

    Stops early if valid.
    """

    state = {"user": user_input, "plan": {}}

    for _ in range(max_loops):

        # --- 1) Itinerary Agent ---
        itinerary = generate_itinerary(user_input)
        if "error" in itinerary:
            return {"error": "invalid_generation", "details": itinerary}

        state["plan"] = itinerary

        # --- 2) Budget Agent ---
        state["plan"] = optimize_budget(state["plan"], user_input["budget"])

        # --- 3) Validation Agent ---
        valid, errors = validate(state["plan"], user_input)

        if valid:
            return state["plan"]

        # If budget impossible / unrealistic
        total = calculate_total(state["plan"])
        if total < user_input["budget"] * 0.1:
            return {"error": "under-costed"}

        # --- 4) Feedback Agent ---
        state = refine_state(state, errors)

    return {"error": "constraints_not_met", "details": state}
