import streamlit as st

from config import GEMINI_API_KEY
from database.db import save_record
from services.gemini_service import ask_assistant
from utils.ui import show_page_heading

show_page_heading(
    "AI Farming Assistant",
    "Optional Gemini-powered answers in Hindi or English, grounded in module data available in this session.",
)
if not GEMINI_API_KEY:
    st.info("Gemini is not configured. Set the GEMINI_API_KEY environment variable and restart Streamlit.")

language = st.selectbox("Response language", ["English", "Hindi"])
question = st.text_area("Ask a farming question")
if st.button("Ask AgroMind", type="primary"):
    context = {
        "soil_analysis": st.session_state.get("soil_result"),
        "crop_recommendation": st.session_state.get("crop_result"),
        "disease_detection": st.session_state.get("disease_result"),
        "weather": st.session_state.get("weather_result"),
        "climate_risks": st.session_state.get("climate_risks"),
        "irrigation": st.session_state.get("irrigation_result"),
        "farm_risk": st.session_state.get("risk_result"),
    }
    try:
        answer = ask_assistant(question, context, language)
        st.session_state["assistant_answer"] = answer
        save_record(
            "ai_conversations",
            {"question": question, "answer": answer, "language": language},
            user_id=st.session_state["authenticated_user"]["id"],
        )
    except (RuntimeError, ValueError, OSError) as exc:
        st.error(f"Could not get an assistant response: {exc}")

if st.session_state.get("assistant_answer"):
    st.markdown(st.session_state["assistant_answer"])
    st.caption("AI responses can be inaccurate. Verify important crop-protection decisions with local experts.")
