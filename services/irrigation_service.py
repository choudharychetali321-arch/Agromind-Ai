"""Explainable irrigation screening estimate based on ET0 and user inputs."""

from utils.constants import IRRIGATION_NOTE
from utils.validators import require_number

DEFAULT_CROP_COEFFICIENT = 1.0


def estimate_irrigation(
    *,
    reference_et0_mm_day: float,
    crop_coefficient: float,
    forecast_rain_mm: float,
    soil_moisture_percent: float,
    moisture_target_percent: float,
) -> dict:
    et0 = require_number("Reference evapotranspiration (ET0)", reference_et0_mm_day, 0, 20)
    kc = require_number("Crop coefficient", crop_coefficient, 0.1, 2.0)
    rain = require_number("Forecast rainfall", forecast_rain_mm, 0, 1000)
    moisture = require_number("Soil moisture", soil_moisture_percent, 0, 100)
    target = require_number("Target moisture", moisture_target_percent, 1, 100)

    daily_crop_use = et0 * kc
    moisture_gap = max(0.0, target - moisture)
    # A percentage-point moisture gap is not converted into mm without soil water-holding data.
    screening_need = max(0.0, daily_crop_use * 3 - min(rain, daily_crop_use * 3))
    if moisture >= target:
        status = "No immediate irrigation trigger from the entered moisture target"
    elif screening_need == 0:
        status = "Rainfall may cover the estimated 3-day crop use; recheck soil moisture"
    else:
        status = "Irrigation may be needed; verify root-zone moisture before applying water"
    return {
        "daily_crop_water_use_mm": daily_crop_use,
        "three_day_screening_need_mm": screening_need,
        "soil_moisture_gap_percentage_points": moisture_gap,
        "status": status,
        "formula": "ETc = ET0 × Kc; 3-day screening need = max(0, 3 × ETc − forecast rainfall)",
        "limitations": IRRIGATION_NOTE
        + " The moisture gap is not converted to millimetres because soil water-holding capacity is unknown.",
    }
