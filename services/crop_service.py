"""Crop inference is enabled only when a trained model artifact is available."""

from pathlib import Path

import numpy as np

from config import TRAINED_MODELS_DIR

FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
MODEL_PATH = TRAINED_MODELS_DIR / "crop_model.joblib"
CLASSES_PATH = TRAINED_MODELS_DIR / "crop_classes.json"


def recommend_crops(values: dict[str, float], model_path: Path = MODEL_PATH) -> list[dict]:
    if not model_path.is_file():
        raise FileNotFoundError(
            "Crop model is not trained. Add the documented crop dataset and run "
            "`python -m models.train_crop_model`."
        )
    try:
        import joblib
    except ImportError as exc:
        raise RuntimeError("Install project requirements to use crop recommendations.") from exc

    model = joblib.load(model_path)
    row = np.array([[float(values[name]) for name in FEATURES]], dtype=float)
    if not hasattr(model, "predict_proba"):
        raise RuntimeError("The saved crop model does not provide suitability probabilities.")
    probabilities = model.predict_proba(row)[0]
    classes = list(model.classes_)
    ranked = sorted(zip(classes, probabilities), key=lambda item: item[1], reverse=True)[:3]
    return [
        {"crop": str(crop), "score": float(score)}
        for crop, score in ranked
    ]
