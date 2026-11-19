import streamlit as st

from services.irrigation_service import estimate_irrigation
from services.risk_engine import assess_farm_risk
from services.weather_service import assess_climate_risks
from utils.ui import show_page_heading

show_page_heading(
    "What-if Farm Simulator",
    "Compare generic screening estimates for baseline and modified weather/water inputs. These are simulations, not forecasts.",
)

with st.form("simulator_form"):
    col1, col2 = st.columns(2)
    with col1:
        baseline_temp = st.number_input("Baseline maximum temperature (°C)", -10.0, 70.0, 28.0)
        baseline_rain = st.number_input("Baseline 7-day rainfall (mm)", 0.0, 1000.0, 40.0)
        baseline_moisture = st.number_input("Baseline soil moisture (%)", 0.0, 100.0, 40.0)
    with col2:
        scenario_temp = st.number_input("Scenario maximum temperature (°C)", -10.0, 70.0, 35.0)
        scenario_rain = st.number_input("Scenario 7-day rainfall (mm)", 0.0, 1000.0, 10.0)
        scenario_moisture = st.number_input("Scenario soil moisture (%)", 0.0, 100.0, 25.0)
    et0 = st.number_input("Reference ET0 (mm/day)", 0.0, 20.0, 5.0)
    kc = st.number_input("Crop coefficient (Kc)", 0.1, 2.0, 1.0)
    moisture_target = st.number_input("Target moisture (%)", 1.0, 100.0, 50.0)
    baseline_irrigation = st.checkbox("Irrigation available in baseline", value=True)
    scenario_irrigation = st.checkbox("Irrigation available in modified scenario", value=False)
    submitted = st.form_submit_button("Compare scenarios", type="primary")


def evaluate_scenario(temperature: float, rainfall: float, moisture: float, irrigation_available: bool) -> dict:
    weather = {
        "max_forecast_temperature_c": temperature,
        "rain_next_7d_mm": rainfall,
    }
    climate_risks = assess_climate_risks(weather)
    irrigation = estimate_irrigation(
        reference_et0_mm_day=et0,
        crop_coefficient=kc,
        forecast_rain_mm=rainfall,
        soil_moisture_percent=moisture,
        moisture_target_percent=moisture_target,
    )
    if not irrigation_available:
        irrigation = dict(irrigation)
        irrigation["status"] = "Irrigation unavailable; " + irrigation["status"]
    risk = assess_farm_risk(climate_risks=climate_risks, irrigation=irrigation)
    return {"risk": risk, "irrigation": irrigation, "climate_risks": climate_risks}


if submitted:
    baseline = evaluate_scenario(baseline_temp, baseline_rain, baseline_moisture, baseline_irrigation)
    modified = evaluate_scenario(scenario_temp, scenario_rain, scenario_moisture, scenario_irrigation)
    st.session_state["simulation_result"] = {"baseline": baseline, "modified": modified}

result = st.session_state.get("simulation_result")
if result:
    left, right = st.columns(2)
    for column, title, scenario in (
        (left, "Baseline", result["baseline"]),
        (right, "Modified scenario", result["modified"]),
    ):
        with column:
            st.subheader(title)
            st.metric("Estimated risk", scenario["risk"]["risk_level"].title())
            st.metric("3-day water screening need", f"{scenario['irrigation']['three_day_screening_need_mm']:.1f} mm")
            for item in scenario["climate_risks"]:
                st.write(f"- {item['level'].title()}: {item['risk']} — {item['reason']}")
            if not scenario["climate_risks"]:
                st.write("- No generic climate threshold triggered.")
    st.warning("Simulation only: rule-based estimates are not weather predictions or guaranteed outcomes.")
else:
    st.info("Set baseline and scenario values, then compare.")
