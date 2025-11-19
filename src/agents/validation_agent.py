from agents.budget_agent import calculate_total

def validate(plan, user):
    errors = []

    if plan.get("duration") != user["duration"]:
        errors.append("duration_mismatch")

    total = calculate_total(plan)
    if total > user["budget"]:
        errors.append("over_budget")

    if "per_day_breakdown" not in plan:
        errors.append("missing_per_day_breakdown")

    if errors:
        return False, errors

    return True, []
