import streamlit as st

from database.db import list_records
from utils.ui import show_page_heading

show_page_heading(
    "Reports & History",
    "View reports saved by your signed-in account on this device.",
)
table_labels = {
    "soil_reports": "Soil reports",
    "crop_recommendations": "Crop recommendations",
    "disease_detections": "Disease detections",
    "weather_records": "Weather records",
    "irrigation_records": "Irrigation records",
    "risk_assessments": "Risk assessments",
    "ai_conversations": "AI conversations",
}
selected = st.selectbox("History type", list(table_labels), format_func=table_labels.get)
try:
    records = list_records(
        selected,
        user_id=st.session_state["authenticated_user"]["id"],
    )
except (ValueError, OSError) as exc:
    st.error(f"Could not load history: {exc}")
    st.stop()

if records:
    rows = [
        {"ID": row["id"], "Created": row["created_at"], "Details": str(row["payload"])}
        for row in records
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)
else:
    st.info("No saved records of this type yet.")
