from services.risk_engine import assess_farm_risk


def test_risk_score_is_missing_when_no_evidence_is_available():
    result = assess_farm_risk()

    assert result["farm_health_score"] is None
    assert result["risk_level"] == "insufficient data"
    assert "soil analysis" in result["missing_information"]


def test_risk_score_uses_only_available_components():
    result = assess_farm_risk(
        climate_risks=[{"level": "high", "reason": "High temperature"}],
        irrigation={"status": "Irrigation unavailable; irrigation may be needed"},
    )

    assert result["farm_health_score"] == 0
    assert result["risk_level"] == "high"
    assert len(result["components"]) == 2
    assert any("irrigation access" in action.lower() for action in result["priority_actions"])


def test_risk_engine_lists_unprovided_factors():
    result = assess_farm_risk()

    assert "weather forecast" in result["missing_information"]
    assert "disease detection" in result["missing_information"]
    assert "water assessment" in result["missing_information"]


def test_risk_engine_derives_climate_risks_from_weather_when_needed():
    result = assess_farm_risk(
        weather={
            "max_forecast_temperature_c": 36,
            "rain_next_7d_mm": 80,
        }
    )

    climate = next(component for component in result["components"] if component["factor"] == "Climate")
    assert climate["level"] == "high"
    assert "36.0°C" in climate["evidence"]
