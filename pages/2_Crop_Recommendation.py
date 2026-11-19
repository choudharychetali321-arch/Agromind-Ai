import json

import streamlit as st

from config import TRAINED_MODELS_DIR
from database.db import save_record
from services.crop_service import recommend_crops
from utils.ui import show_page_heading

show_page_heading(
    "Smart Crop Recommendation",
    "Recommendations are produced by a trained Random Forest model. No prediction is shown until a model is trained.",
)

with st.form("crop_form"):
    c1, c2 = st.columns(2)
    with c1:
        nitrogen = st.number_input("Nitrogen (N)", 0.0, 2000.0, 90.0)
        phosphorus = st.number_input("Phosphorus (P)", 0.0, 2000.0, 42.0)
        potassium = st.number_input("Potassium (K)", 0.0, 2000.0, 43.0)
        ph = st.number_input("Soil pH", 0.0, 14.0, 6.5)
    with c2:
        temperature = st.number_input("Air temperature (°C)", -10.0, 70.0, 25.0)
        humidity = st.number_input("Humidity (%)", 0.0, 100.0, 70.0)
        rainfall = st.number_input("Rainfall (mm)", 0.0, 10000.0, 100.0)
    submitted = st.form_submit_button("Recommend crops", type="primary")

if submitted:
    inputs = {
        "N": nitrogen,
        "P": phosphorus,
        "K": potassium,
        "temperature": temperature,
        "humidity": humidity,
        "ph": ph,
        "rainfall": rainfall,
    }
    try:
        recommendations = recommend_crops(inputs)
        result = {"inputs": inputs, "recommendations": recommendations}
        st.session_state["crop_result"] = result
        save_record(
            "crop_recommendations",
            result,
            user_id=st.session_state["authenticated_user"]["id"],
        )
    except (FileNotFoundError, RuntimeError, ValueError, OSError) as exc:
        st.error(str(exc))

result = st.session_state.get("crop_result")
if result:
    st.subheader("Top model recommendations")
    for index, item in enumerate(result["recommendations"], start=1):
        st.metric(f"{index}. {item['crop']}", f"{item['score']:.1%} model score")
    st.caption(
        "Scores are model class probabilities, not guaranteed yield or success. "
        "Confirm suitability with local agronomic guidance."
    )
    metrics_path = TRAINED_MODELS_DIR / "crop_metrics.json"
    if metrics_path.exists():
        try:
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            st.caption(f"Saved held-out test accuracy: {metrics['test_accuracy']:.1%} ({metrics['test_samples']} samples).")
        except (OSError, KeyError, json.JSONDecodeError):
            st.warning("Saved model evaluation metadata could not be read.")
