"""Transparent soil screening; not a substitute for a calibrated laboratory report."""

from utils.constants import SOIL_NPK_UNITS, SOIL_SCREENING_NOTE
from utils.validators import require_number

NUTRIENT_BANDS = {
    "nitrogen": (20.0, 40.0),
    "phosphorus": (10.0, 25.0),
    "potassium": (100.0, 200.0),
}


def analyze_soil(
    *,
    ph: float,
    nitrogen: float,
    phosphorus: float,
    potassium: float,
    moisture: float,
    temperature: float,
    organic_carbon: float | None = None,
) -> dict:
    values = {
        "pH": require_number("Soil pH", ph, 0, 14),
        "Nitrogen": require_number("Nitrogen", nitrogen, 0, 10000),
        "Phosphorus": require_number("Phosphorus", phosphorus, 0, 10000),
        "Potassium": require_number("Potassium", potassium, 0, 10000),
        "Soil moisture (%)": require_number("Soil moisture", moisture, 0, 100),
        "Soil temperature (°C)": require_number("Soil temperature", temperature, -10, 70),
    }
    if organic_carbon is not None:
        values["Organic carbon (%)"] = require_number(
            "Organic carbon", organic_carbon, 0, 100
        )

    findings: list[str] = []
    if ph < 5.5:
        findings.append("Soil is strongly acidic by this screening rule; confirm before liming.")
    elif ph < 6.0:
        findings.append("Soil is mildly acidic; check crop-specific pH needs.")
    elif ph > 8.0:
        findings.append("Soil is strongly alkaline by this screening rule; confirm before treatment.")
    elif ph > 7.5:
        findings.append("Soil is mildly alkaline; check crop-specific nutrient availability.")
    else:
        findings.append("pH is within the broad 6.0–7.5 screening range.")

    nutrient_status = {}
    for nutrient, (low, adequate) in NUTRIENT_BANDS.items():
        amount = values[nutrient.title()]
        if amount < low:
            status = "below screening band"
            findings.append(f"{nutrient.title()} is below the broad screening band.")
        elif amount < adequate:
            status = "within lower screening band"
        else:
            status = "at or above screening band"
        nutrient_status[nutrient] = status

    if moisture < 20:
        findings.append("Moisture is low by the broad screening rule; verify with a calibrated sensor.")
    elif moisture > 80:
        findings.append("Moisture is high; check drainage and avoid unnecessary irrigation.")
    else:
        findings.append("Moisture is within the broad 20–80% screening range.")

    deficiencies = [name for name, status in nutrient_status.items() if status == "below screening band"]
    condition = "Review recommended" if deficiencies or ph < 5.5 or ph > 8 else "No major screening flag"
    return {
        "values": values,
        "nutrient_status": nutrient_status,
        "potential_deficiencies": deficiencies,
        "condition": condition,
        "findings": findings,
        "units": SOIL_NPK_UNITS,
        "limitations": SOIL_SCREENING_NOTE,
    }
