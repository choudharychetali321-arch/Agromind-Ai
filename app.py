"""AgroMind AI web application and authenticated page router."""

import streamlit as st

from database.db import initialize_database
from utils.auth_ui import current_user, logout_user, show_login

st.set_page_config(page_title="AgroMind AI", page_icon="🌱", layout="wide")
initialize_database()
user = current_user()

st.markdown(
    """
    <style>
    :root {
      color-scheme: light;
      --agro-text: #173b2a;
      --agro-muted: #40594a;
      --agro-green: #16834a;
      --agro-border: #c8d9cc;
    }
    html, body, [class*="st-"], [data-testid="stAppViewContainer"] {
      color: var(--agro-text);
    }
    .stApp { background: linear-gradient(180deg, #f3fbf5 0%, #ffffff 45%); }
    [data-testid="stSidebar"] { background-color: #eaf3ec; }
    [data-testid="stSidebar"] * { color: var(--agro-text); }
    [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p,
    [data-testid="stCaptionContainer"],
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"],
    [data-testid="stMetricDelta"] {
      color: var(--agro-text) !important;
      opacity: 1 !important;
    }
    [data-testid="stCaptionContainer"] { color: var(--agro-muted) !important; }
    input, textarea, [data-baseweb="select"] > div {
      color: var(--agro-text) !important;
      background-color: #ffffff !important;
    }
    input::placeholder, textarea::placeholder { color: #607466 !important; }
    [data-testid="stMetric"] {
      color: var(--agro-text);
      background: #ffffff;
      border: 1px solid var(--agro-border);
      border-radius: 12px;
      padding: 14px;
    }
    button[data-testid*="primary"] {
      background-color: var(--agro-green) !important;
      border-color: var(--agro-green) !important;
      color: #ffffff !important;
    }
    button[data-testid*="primary"] *,
    button[data-testid*="primary"]:hover * { color: #ffffff !important; }
    a { color: #12663b; }
    div[data-testid="stMetric"] {
      background: #ffffff;
      border-color: var(--agro-border);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if user is None:
    login_navigation = st.navigation(
        [st.Page(show_login, title="Sign in", icon="🔐")],
        position="hidden",
    )
    login_navigation.run()
    st.stop()

st.sidebar.caption(f"Signed in as {user['email']}")
if st.sidebar.button("Sign out", use_container_width=True):
    logout_user()
    st.rerun()

pages = {
    "Farm workspace": [
        st.Page("pages/0_Dashboard.py", title="Dashboard", icon="🌱", default=True),
        st.Page("pages/1_Soil_Intelligence.py", title="Soil Intelligence", icon="🧪"),
        st.Page("pages/2_Crop_Recommendation.py", title="Crop Recommendation", icon="🌾"),
        st.Page("pages/3_Disease_Detection.py", title="Disease Detection", icon="🍃"),
        st.Page("pages/4_Climate_Intelligence.py", title="Climate Intelligence", icon="🌦️"),
        st.Page("pages/5_Water_Management.py", title="Water Management", icon="💧"),
        st.Page("pages/6_Farm_Risk_Engine.py", title="Farm Risk Engine", icon="🛡️"),
        st.Page("pages/7_What_If_Simulator.py", title="What-if Simulator", icon="🔬"),
        st.Page("pages/8_AI_Assistant.py", title="AI Farming Assistant", icon="💬"),
        st.Page("pages/9_Reports_History.py", title="Reports & History", icon="📋"),
    ]
}
navigation = st.navigation(pages)
navigation.run()
