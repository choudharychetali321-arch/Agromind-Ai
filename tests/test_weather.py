import pytest

from services.weather_service import assess_climate_risks
from utils.validators import validate_coordinates


def test_coordinate_validation_rejects_invalid_longitude():
    with pytest.raises(ValueError, match="Longitude"):
        validate_coordinates(20, 181)


def test_climate_risks_use_forecast_thresholds():
    risks = assess_climate_risks(
        {"max_forecast_temperature_c": 36, "rain_next_7d_mm": 5}
    )

    assert [risk["level"] for risk in risks] == ["high", "high"]
    assert "Heat stress" in risks[0]["risk"]
    assert "drought" in risks[1]["risk"].lower()
