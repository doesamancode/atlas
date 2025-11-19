def validate(plan, user):
    """
    Ultra-Pro validation for ATLAS:

    Accepts:
    - multi-city accommodations via "city_accommodations"
    - old single accommodation block (fallback)
    - per-day breakdown must exist with at least 1 day
    - transport must exist
    - budget check is soft (no hard failures)

    Returns:
        (is_valid: bool, errors: list)
    """

    errors = []

    # 🔍 Per-day breakdown must exist
    if "per_day_breakdown" not in plan:
        errors.append("missing_per_day_data")
    else:
        if not isinstance(plan["per_day_breakdown"], list) or len(plan["per_day_breakdown"]) == 0:
            errors.append("empty_per_day")

    # 🔍 Validate accommodations
    if "city_accommodations" in plan:
        if not isinstance(plan["city_accommodations"], list) or len(plan["city_accommodations"]) == 0:
            errors.append("invalid_city_accommodations")
        else:
            # Ensure each entry has city + hotel
            for entry in plan["city_accommodations"]:
                if not entry.get("hotel") or not entry.get("city"):
                    errors.append("missing_city_hotel")
    else:
        # fallback structure
        if "accommodation" not in plan:
            errors.append("missing_accommodation")

    # 🔍 Validate transport section
    if "transport" not in plan:
        errors.append("missing_transport")

    # 🔍 Budget checks (soft)
    est_acc = 0
    if "city_accommodations" in plan:
        est_acc = sum([ac.get("estimated_cost", 0) for ac in plan["city_accommodations"]])
    else:
        est_acc = plan.get("accommodation", {}).get("estimated_cost", 0)

    est_transport = plan.get("transport", {}).get("estimated_cost", 0)
    total_est = est_acc + est_transport

    if total_est > user["budget"] * 1.7:
        errors.append("budget_too_high")

    # 🔍 Final verdict
    return (len(errors) == 0, errors)
