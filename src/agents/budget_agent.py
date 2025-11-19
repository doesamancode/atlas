def calculate_total(plan):
    """
    Calculate an estimated total cost combining:
    - per-day costs
    - accommodation (multi-city or single)
    - transport
    """
    total = 0

    # Per-day costs
    for day in plan.get("per_day_breakdown", []):
        total += day.get("estimated_cost", 0)

    # Multi-city accommodation
    if "city_accommodations" in plan:
        total += sum([ac.get("estimated_cost", 0) for ac in plan["city_accommodations"]])
    else:
        total += plan.get("accommodation", {}).get("estimated_cost", 0)

    # Transport
    total += plan.get("transport", {}).get("estimated_cost", 0)

    return total


def optimize_budget(plan, budget):
    """
    BudgetAgent tries to adjust costs softly.
    No deep optimization — just normalization if wildly off.
    """

    total = calculate_total(plan)

    # If cost massively exceeds budget → shrink estimates
    if total > budget * 2:
        factor = budget * 1.4 / total  # soften aggressively
    elif total > budget * 1.3:
        factor = budget * 1.1 / total  # small normalization
    else:
        factor = 1  # cost acceptable

    # Apply normalization factor
    for day in plan.get("per_day_breakdown", []):
        cost = day.get("estimated_cost", 0)
        day["estimated_cost"] = int(cost * factor)

    if "city_accommodations" in plan:
        for ac in plan["city_accommodations"]:
            cost = ac.get("estimated_cost", 0)
            ac["estimated_cost"] = int(cost * factor)
    else:
        acc_cost = plan.get("accommodation", {}).get("estimated_cost", 0)
        plan["accommodation"]["estimated_cost"] = int(acc_cost * factor)

    trans_cost = plan.get("transport", {}).get("estimated_cost", 0)
    plan["transport"]["estimated_cost"] = int(trans_cost * factor)

    return plan
