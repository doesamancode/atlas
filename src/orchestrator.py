from agents.itinerary_agent import generate_itinerary
from agents.budget_agent import optimize_budget, calculate_total
from agents.validation_agent import validate
from agents.feedback_agent import refine_state

def run_agentic_pipeline(source, destinations, duration, budget, travelers, max_loops=2):
    """
    Agentic pipeline for ATLAS (multi-step reasoning workflow).

    1. ItineraryAgent → structured multi-city itinerary
    2. BudgetAgent → adjust/optimize soft cost distribution
    3. ValidationAgent → checks structure, fields, cost realism
    4. FeedbackAgent → refine based on detected issues

    Returns final valid plan OR an error package.
    """

    # Normalize input into a single dict for all agents
    user_input = {
        "source": source,
        "destinations": destinations,
        "duration": duration,
        "budget": budget,
        "travelers": travelers,
    }

    state = {"user": user_input, "plan": {}}

    for _ in range(max_loops):

        # --- 1) ITINERARY AGENT ---
        itinerary = generate_itinerary(user_input)

        if "error" in itinerary:
            # LLM failed or incomplete generation
            return {"error": "invalid_generation", "details": itinerary}

        state["plan"] = itinerary

        # --- 2) BUDGET AGENT ---
        state["plan"] = optimize_budget(state["plan"], user_input["budget"])

        # --- 3) VALIDATION AGENT ---
        valid, errors = validate(state["plan"], user_input)

        if valid:
            return state["plan"]  # SUCCESS ✓

        # Hard fail condition (under-costed)
        total = calculate_total(state["plan"])
        if total < user_input["budget"] * 0.1:
            return {"error": "under_costed"}

        # --- 4) FEEDBACK AGENT (refinement loop) ---
        state = refine_state(state, errors)

    # If after refinement loops it's still invalid
    return {"error": "constraints_not_met", "details": state}
