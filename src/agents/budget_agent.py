def calculate_total(plan):
    total = 0

    for day in plan.get("per_day_breakdown", []):
        try:
            total += int(day.get("estimated_cost", 0))
        except:
            pass

    try:
        total += int(plan.get("accommodation", {}).get("estimated_cost", 0))
        total += int(plan.get("transport", {}).get("estimated_cost", 0))
    except:
        pass

    return total


def optimize_budget(plan, limit):
    total = calculate_total(plan)

    if total <= limit:
        return plan

    excess = total - limit
    per_day = plan.get("per_day_breakdown", [])

    if len(per_day) == 0:
        return plan

    reduce_per_day = excess // len(per_day)

    for day in per_day:
        cost = int(day.get("estimated_cost", 0))
        day["estimated_cost"] = max(0, cost - reduce_per_day)

    return plan
