import streamlit as st

from database.db import save_record
from services.risk_engine import assess_farm_risk
from utils.ui import show_page_heading

show_page_heading(
    "Farm Risk Intelligence",
    "Combines only module results currently available in this browser session; missing inputs remain visible.",
)

if st.button("Assess available farm data", type="primary"):
    result = assess_farm_risk(
        soil=st.session_state.get("soil_result"),
        weather=st.session_state.get("weather_result"),
        climate_risks=st.session_state.get("climate_risks"),
        disease=st.session_state.get("disease_result"),
        irrigation=st.session_state.get("irrigation_result"),
    )
    st.session_state["risk_result"] = result
    try:
        save_record(
            "risk_assessments",
            result,
            user_id=st.session_state["authenticated_user"]["id"],
        )
    except OSError as exc:
        st.error(f"Assessment created but could not be saved: {exc}")

result = st.session_state.get("risk_result")
if result:
    if result["farm_health_score"] is None:
        st.warning("Insufficient data to calculate a farm health score.")
    else:
        col1, col2 = st.columns(2)
        col1.metric("Farm health score", f"{result['farm_health_score']} / 100")
        col2.metric("Current risk level", result["risk_level"].title())
    st.caption(result["scoring_method"])
    st.subheader("Evidence by factor")
    if result["components"]:
        st.dataframe(result["components"], use_container_width=True, hide_index=True)
    else:
        st.info("No measurable module results are available yet.")
    st.subheader("Priority actions")
    for action in result["priority_actions"]:
        st.write(f"- {action}")
    st.subheader("Missing information")
    if result["missing_information"]:
        for item in result["missing_information"]:
            st.write(f"- {item}")
    else:
        st.success("All supported factors in this assessment have data.")
else:
    st.info("Run soil, climate, water, or disease modules first, then assess available data.")
