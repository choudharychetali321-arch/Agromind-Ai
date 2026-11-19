import pytest

from services.irrigation_service import estimate_irrigation


def test_irrigation_estimate_explains_its_computation():
    result = estimate_irrigation(
        reference_et0_mm_day=5,
        crop_coefficient=1,
        forecast_rain_mm=4,
        soil_moisture_percent=35,
        moisture_target_percent=50,
    )

    assert result["daily_crop_water_use_mm"] == 5
    assert result["three_day_screening_need_mm"] == 11
    assert result["soil_moisture_gap_percentage_points"] == 15
    assert "ETc = ET0 × Kc" in result["formula"]


def test_irrigation_rejects_invalid_coefficient():
    with pytest.raises(ValueError, match="Crop coefficient"):
        estimate_irrigation(
            reference_et0_mm_day=5,
            crop_coefficient=3,
            forecast_rain_mm=0,
            soil_moisture_percent=30,
            moisture_target_percent=50,
        )
