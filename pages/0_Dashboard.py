import streamlit as st

st.title("🌱 AgroMind AI")
st.subheader("Predict the Risk. Protect the Crop. Optimize Every Resource.")
st.write(
    "An agricultural decision-support workspace for soil screening, crop planning, "
    "weather awareness, and water management."
)
st.info(
    "Soil, climate, and water features use transparent screening estimates. Crop and disease "
    "predictions need real datasets and trained models; the app never fabricates results."
)

st.header("Your farm intelligence workspace")
col1, col2, col3 = st.columns(3)
with col1:
    st.page_link("pages/1_Soil_Intelligence.py", label="🧪 Soil Intelligence", use_container_width=True)
    st.page_link("pages/2_Crop_Recommendation.py", label="🌾 Crop Recommendation", use_container_width=True)
    st.page_link("pages/3_Disease_Detection.py", label="🍃 Disease Detection", use_container_width=True)
with col2:
    st.page_link("pages/4_Climate_Intelligence.py", label="🌦️ Climate Intelligence", use_container_width=True)
    st.page_link("pages/5_Water_Management.py", label="💧 Water Management", use_container_width=True)
    st.page_link("pages/6_Farm_Risk_Engine.py", label="🛡️ Farm Risk Engine", use_container_width=True)
with col3:
    st.page_link("pages/7_What_If_Simulator.py", label="🔬 What-if Simulator", use_container_width=True)
    st.page_link("pages/8_AI_Assistant.py", label="💬 AI Farming Assistant", use_container_width=True)
    st.page_link("pages/9_Reports_History.py", label="📋 Reports & History", use_container_width=True)

st.divider()
left, right = st.columns([1.3, 1])
with left:
    st.subheader("Built for evidence-based decisions")
    st.write(
        "Each module shows its assumptions and limitations. Missing measurements are listed "
        "rather than silently guessed, and model-backed results require trained artifacts."
    )
with right:
    st.subheader("Project status")
    st.write("Soil screening: available")
    st.write("Open-Meteo weather: available when online")
    st.write("Crop and disease ML: requires local dataset and training")
    st.write("Gemini assistant: requires `GEMINI_API_KEY`")
