import pytest

from services.soil_service import analyze_soil


def valid_soil(**updates):
    values = {
        "ph": 6.5,
        "nitrogen": 40,
        "phosphorus": 20,
        "potassium": 150,
        "moisture": 45,
        "temperature": 24,
    }
    values.update(updates)
    return values


def test_soil_analysis_reports_measured_values_and_screening_flags():
    result = analyze_soil(**valid_soil(nitrogen=5, ph=5.0))

    assert result["condition"] == "Review recommended"
    assert result["potential_deficiencies"] == ["nitrogen"]
    assert any("strongly acidic" in finding for finding in result["findings"])
    assert result["values"]["Nitrogen"] == 5


def test_soil_analysis_rejects_out_of_range_ph():
    with pytest.raises(ValueError, match="Soil pH"):
        analyze_soil(**valid_soil(ph=15))
