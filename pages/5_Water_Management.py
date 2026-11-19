import streamlit as st

from database.db import save_record
from services.irrigation_service import DEFAULT_CROP_COEFFICIENT, estimate_irrigation
from utils.constants import IRRIGATION_NOTE
from utils.ui import show_page_heading

show_page_heading(
    "Smart Water Management",
    "A transparent screening estimate. Enter reference evapotranspiration (ET0) from a trusted local source if available.",
)
weather = st.session_state.get("weather_result", {})
default_rain = min(float(weather.get("rain_next_7d_mm", 0.0)), 1000.0)

with st.form("irrigation_form"):
    col1, col2 = st.columns(2)
    et0 = col1.number_input("Reference ET0 (mm/day)", min_value=0.0, max_value=20.0, value=5.0, step=0.1)
    crop_coefficient = col2.number_input("Crop coefficient (Kc)", min_value=0.1, max_value=2.0, value=DEFAULT_CROP_COEFFICIENT, step=0.05)
    rainfall = col1.number_input("Forecast rainfall (mm, next 3 days)", min_value=0.0, max_value=1000.0, value=default_rain, step=1.0)
    moisture = col2.number_input("Current soil moisture (%)", min_value=0.0, max_value=100.0, value=40.0, step=1.0)
    target = col1.number_input("Target soil moisture (%)", min_value=1.0, max_value=100.0, value=50.0, step=1.0)
    submitted = st.form_submit_button("Estimate water need", type="primary")

if submitted:
    try:
        result = estimate_irrigation(
            reference_et0_mm_day=et0,
            crop_coefficient=crop_coefficient,
            forecast_rain_mm=rainfall,
            soil_moisture_percent=moisture,
            moisture_target_percent=target,
        )
        st.session_state["irrigation_result"] = result
        save_record(
            "irrigation_records",
            result,
            user_id=st.session_state["authenticated_user"]["id"],
        )
    except (ValueError, OSError) as exc:
        st.error(f"Could not estimate irrigation: {exc}")

result = st.session_state.get("irrigation_result")
if result:
    st.subheader(result["status"])
    c1, c2 = st.columns(2)
    c1.metric("Estimated crop use", f"{result['daily_crop_water_use_mm']:.1f} mm/day")
    c2.metric("3-day screening need", f"{result['three_day_screening_need_mm']:.1f} mm")
    st.write(f"**Method:** {result['formula']}")
    st.caption(result["limitations"])
    st.caption("Estimate saved to local history.")
else:
    st.info(IRRIGATION_NOTE)
