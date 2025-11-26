from agents.itinerary_agent import generate_itinerary
from agents.budget_agent import optimize_budget, calculate_total
from agents.validation_agent import validate
from agents.feedback_agent import refine_state

def run_agentic_pipeline(source, destinations, duration, budget, travelers, max_loops=2):
    """
    Agentic pipeline for ATLAS (multi-step reasoning workflow).

    Flow:
    1) ItineraryAgent  → Base plan
    2) BudgetAgent     → Soft cost optimization
    3) ValidationAgent → Structural & feasibility checks
    4) FeedbackAgent   → Auto refinements (if needed)
    """

    user_input = {
        "source": source,
        "destinations": destinations,
        "duration": duration,
        "budget": budget,
        "travelers": travelers,
    }

    state = {"user": user_input, "plan": {}}

    for _ in range(max_loops):
        # ---- 1️⃣ Itinerary Agent ----
        itinerary = generate_itinerary(user_input)
        if "error" in itinerary:
            return {"error": "invalid_generation", "details": itinerary}

        state["plan"] = itinerary

        # ---- 2️⃣ Budget Agent ----
        state["plan"] = optimize_budget(state["plan"], budget)
        total = calculate_total(state["plan"])

        # Under-budget sanity
        if total < budget * 0.10:
            return {"error": "under_costed", "total_cost": total}

        # ---- 3️⃣ Validation Agent ----
        valid, errors = validate(state["plan"], user_input)

        if valid:
            return state["plan"]  # 🎯 SUCCESS

        # ---- 4️⃣ Feedback Agent ----
        state = refine_state(state, errors)

    # ♻ After max refinement attempts → FAIL WITH REASONS
    return {"error": "validation_failed", "reasons": errors}
