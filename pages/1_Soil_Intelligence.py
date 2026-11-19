import streamlit as st

from database.db import save_record
from services.soil_service import analyze_soil
from utils.ui import show_page_heading

show_page_heading(
    "Soil Intelligence",
    "Enter measured soil values for a transparent screening report. N-P-K defaults are broad demo bands.",
)

with st.form("soil_form"):
    col1, col2 = st.columns(2)
    with col1:
        ph = st.number_input("Soil pH", min_value=0.0, max_value=14.0, value=6.5, step=0.1)
        nitrogen = st.number_input("Nitrogen (mg/kg)", min_value=0.0, value=40.0, step=1.0)
        phosphorus = st.number_input("Phosphorus (mg/kg)", min_value=0.0, value=20.0, step=1.0)
        potassium = st.number_input("Potassium (mg/kg)", min_value=0.0, value=150.0, step=1.0)
    with col2:
        moisture = st.number_input("Soil moisture (%)", min_value=0.0, max_value=100.0, value=45.0, step=1.0)
        temperature = st.number_input("Soil temperature (°C)", min_value=-10.0, max_value=70.0, value=24.0, step=0.5)
        organic_carbon = st.number_input("Organic carbon (%) — optional; use 0 if unknown", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
    submitted = st.form_submit_button("Analyze soil", type="primary")

if submitted:
    try:
        result = analyze_soil(
            ph=ph,
            nitrogen=nitrogen,
            phosphorus=phosphorus,
            potassium=potassium,
            moisture=moisture,
            temperature=temperature,
            organic_carbon=organic_carbon if organic_carbon > 0 else None,
        )
        st.session_state["soil_result"] = result
        save_record(
            "soil_reports",
            result,
            user_id=st.session_state["authenticated_user"]["id"],
        )
    except (ValueError, OSError) as exc:
        st.error(f"Could not analyze or save soil report: {exc}")

result = st.session_state.get("soil_result")
if result:
    st.subheader(result["condition"])
    if result["potential_deficiencies"]:
        st.warning("Potential screening flags: " + ", ".join(result["potential_deficiencies"]))
    st.markdown("#### Findings")
    for finding in result["findings"]:
        st.write(f"- {finding}")
    st.caption(result["limitations"])
    st.caption("Report saved to local SQLite history.")
else:
    st.info("Submit measured values to generate your first soil report.")
