import streamlit as st

from database.db import save_record
from services.weather_service import assess_climate_risks, get_weather
from utils.ui import show_page_heading

show_page_heading(
    "Climate Intelligence",
    "Current conditions and a seven-day forecast from Open-Meteo, with separate generic agricultural risk screening.",
)

with st.form("weather_form"):
    col1, col2 = st.columns(2)
    latitude = col1.number_input("Latitude", min_value=-90.0, max_value=90.0, value=20.0, step=0.01, format="%.4f")
    longitude = col2.number_input("Longitude", min_value=-180.0, max_value=180.0, value=78.0, step=0.01, format="%.4f")
    submitted = st.form_submit_button("Get weather", type="primary")

if submitted:
    try:
        weather = get_weather(latitude, longitude)
        climate_risks = assess_climate_risks(weather)
        st.session_state["weather_result"] = weather
        st.session_state["climate_risks"] = climate_risks
        save_record(
            "weather_records",
            weather,
            user_id=st.session_state["authenticated_user"]["id"],
        )
    except (RuntimeError, ValueError, OSError) as exc:
        st.error(f"Could not retrieve weather: {exc}")

weather = st.session_state.get("weather_result")
if weather:
    st.caption(f"Open-Meteo observation time: {weather['observed_at']} ({weather['timezone']})")
    cols = st.columns(4)
    cols[0].metric("Temperature", f"{weather['temperature_c']:.1f} °C")
    cols[1].metric("Humidity", f"{weather['humidity_percent']:.0f}%")
    cols[2].metric("Current precipitation", f"{weather['current_precipitation_mm']:.1f} mm")
    cols[3].metric("Rain forecast (7 days)", f"{weather['rain_next_7d_mm']:.1f} mm")
    forecast = weather["forecast"]
    st.line_chart(
        forecast,
        x="date",
        y=["temperature_max_c", "temperature_min_c"],
    )
    st.bar_chart(forecast, x="date", y="precipitation_mm")
    climate_risks = st.session_state.get("climate_risks", [])
    st.subheader("Agricultural risk screening")
    if climate_risks:
        for risk in climate_risks:
            st.warning(f"**{risk['level'].title()} — {risk['risk']}:** {risk['reason']}")
    else:
        st.success("No generic climate threshold was triggered for this forecast.")
    st.caption(weather["risk_note"])
else:
    st.info("Enter farm coordinates to retrieve a forecast. Internet access is required.")
