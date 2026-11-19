import json

import streamlit as st

from config import TRAINED_MODELS_DIR
from database.db import save_record
from services.disease_service import predict_disease
from utils.ui import show_page_heading

show_page_heading(
    "Crop Disease Detection",
    "Upload a clear leaf photo. Predictions require a trained MobileNetV2 model and only cover its documented classes.",
)

uploaded = st.file_uploader("Leaf image", type=["jpg", "jpeg", "png"])
if uploaded and st.button("Analyze image", type="primary"):
    try:
        result = predict_disease(uploaded.getvalue())
        st.session_state["disease_result"] = result
        save_record(
            "disease_detections",
            result,
            user_id=st.session_state["authenticated_user"]["id"],
        )
    except (FileNotFoundError, RuntimeError, ValueError, OSError) as exc:
        st.error(str(exc))

result = st.session_state.get("disease_result")
if uploaded:
    st.image(uploaded, caption="Uploaded image", width=360)
if result:
    if result["status"] == "uncertain":
        st.warning(result["message"])
    else:
        st.subheader(result["label"])
        st.metric("Model confidence", f"{result['confidence']:.1%}")
        st.info(result["message"])
        st.warning(
            "This model output is not a confirmed diagnosis. Check the plant and consult a local "
            "agricultural expert before applying treatment."
        )
    metrics_path = TRAINED_MODELS_DIR / "disease_metrics.json"
    if metrics_path.exists():
        try:
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            st.caption(f"Saved held-out test accuracy: {metrics['test_accuracy']:.1%}.")
        except (OSError, KeyError, json.JSONDecodeError):
            st.warning("Saved disease-model evaluation metadata could not be read.")
elif not uploaded:
    st.info("Upload a supported image to begin. If the model or image classes are not available, no prediction is generated.")
