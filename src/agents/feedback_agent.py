def refine_state(state, errors):
    plan = state["plan"]

    # Simple fixes for now (quickest agentic mode)
    if "duration_mismatch" in errors:
        plan["duration"] = state["user"]["duration"]

    if "missing_per_day_breakdown" in errors:
        plan["per_day_breakdown"] = []

    state["plan"] = plan
    return state
