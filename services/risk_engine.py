"""Explainable risk summary using only supplied measurements and module outputs."""

from services.weather_service import assess_climate_risks

def assess_farm_risk(
    *,
    soil: dict | None = None,
    weather: dict | None = None,
    climate_risks: list[dict] | None = None,
    disease: dict | None = None,
    irrigation: dict | None = None,
) -> dict:
    components: list[dict] = []
    actions: list[str] = []
    missing = []
    if weather is not None and climate_risks is None:
        climate_risks = assess_climate_risks(weather)

    if soil:
        ph = float(soil["values"]["pH"])
        if ph < 5.5 or ph > 8:
            level, points = "high", 0
            actions.append("Confirm soil pH with a local lab before making an amendment.")
        elif ph < 6 or ph > 7.5:
            level, points = "moderate", 50
            actions.append("Check soil pH against the selected crop's preferred range.")
        else:
            level, points = "low", 100
        components.append({"factor": "Soil pH", "level": level, "health_points": points, "evidence": f"Measured pH: {ph:g}."})
        if soil.get("potential_deficiencies"):
            components.append(
                {
                    "factor": "Nutrient screening",
                    "level": "moderate",
                    "health_points": 50,
                    "evidence": "Potential low nutrients: " + ", ".join(soil["potential_deficiencies"]),
                }
            )
            actions.append("Confirm nutrient screening flags with a calibrated soil test.")
    else:
        missing.append("soil analysis")

    if climate_risks is not None:
        levels = [item["level"] for item in climate_risks]
        level = "high" if "high" in levels else ("moderate" if "moderate" in levels else "low")
        points = {"high": 0, "moderate": 50, "low": 100}[level]
        evidence = "; ".join(item["reason"] for item in climate_risks) or "No generic climate threshold was triggered."
        components.append({"factor": "Climate", "level": level, "health_points": points, "evidence": evidence})
        if climate_risks:
            actions.append("Review the weather alerts and adjust field operations for the forecast.")
    else:
        missing.append("weather forecast")

    if disease:
        if disease.get("status") == "uncertain":
            missing.append("reliable disease result (image result was uncertain)")
        elif disease.get("status") == "prediction":
            healthy = disease.get("is_healthy")
            level, points = ("low", 100) if healthy else ("high", 0)
            components.append(
                {
                    "factor": "Leaf image model",
                    "level": level,
                    "health_points": points,
                    "evidence": f"Predicted class: {disease['label']} ({disease['confidence']:.0%} confidence).",
                }
            )
            if not healthy:
                actions.append("Inspect affected plants and seek local expert confirmation before treatment.")
    else:
        missing.append("disease detection")

    if irrigation:
        status = irrigation["status"]
        if "unavailable" in status.lower():
            level, points = "high", 0
            actions.append("Arrange irrigation access or update the plan based on available water.")
        elif "may be needed" in status:
            level, points = "moderate", 50
            actions.append("Check root-zone moisture and rainfall before irrigation.")
        else:
            level, points = "low", 100
        components.append({"factor": "Water status", "level": level, "health_points": points, "evidence": status})
    else:
        missing.append("water assessment")

    score = round(sum(item["health_points"] for item in components) / len(components)) if components else None
    risk_level = (
        "insufficient data" if score is None else
        "high" if score < 40 else
        "moderate" if score < 75 else "low"
    )
    return {
        "farm_health_score": score,
        "risk_level": risk_level,
        "components": components,
        "missing_information": missing,
        "priority_actions": list(dict.fromkeys(actions)) or ["Continue monitoring and update the assessment when conditions change."],
        "scoring_method": (
            "Each available component receives 0 (high risk), 50 (moderate risk), or 100 "
            "(low risk); the displayed score is the unweighted mean of available components. "
            "Missing components are excluded and listed, so the score is not a complete-farm guarantee."
        ),
    }
