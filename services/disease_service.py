"""Disease inference is enabled only when a trained image model is available."""

import json
from io import BytesIO
import re

from config import TRAINED_MODELS_DIR

MODEL_PATH = TRAINED_MODELS_DIR / "disease_model.keras"
CLASSES_PATH = TRAINED_MODELS_DIR / "disease_classes.json"
CONFIDENCE_THRESHOLD = 0.60
MAX_IMAGE_BYTES = 10 * 1024 * 1024


def _is_healthy_class(label: str) -> bool:
    return "healthy" in re.findall(r"[a-z]+", label.lower())


def predict_disease(image_bytes: bytes) -> dict:
    if not image_bytes:
        raise ValueError("The uploaded image is empty.")
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise ValueError("Image must be 10 MB or smaller.")
    if not MODEL_PATH.is_file() or not CLASSES_PATH.is_file():
        raise FileNotFoundError(
            "Disease model is not trained. Prepare the documented image dataset and run "
            "`python -m models.train_disease_model`."
        )
    try:
        import numpy as np
        import tensorflow as tf
    except ImportError as exc:
        raise RuntimeError("Install project requirements to use disease detection.") from exc

    try:
        image = tf.keras.utils.load_img(BytesIO(image_bytes), target_size=(224, 224))
    except (ValueError, OSError) as exc:
        raise ValueError("Could not read this image. Upload a valid JPEG or PNG leaf photo.") from exc

    classes = json.loads(CLASSES_PATH.read_text(encoding="utf-8"))
    if not isinstance(classes, list) or not classes:
        raise RuntimeError("Disease class metadata is missing or invalid.")
    model = tf.keras.models.load_model(MODEL_PATH)
    array = tf.keras.utils.img_to_array(image)
    # The trained model includes its own MobileNetV2 preprocessing layer.
    probabilities = model.predict(np.expand_dims(array, axis=0), verbose=0)[0]
    if (
        len(probabilities) != len(classes)
        or not np.all(np.isfinite(probabilities))
        or np.any(probabilities < 0)
    ):
        raise RuntimeError("Disease model output does not match its saved class metadata.")
    index = int(np.argmax(probabilities))
    confidence = float(probabilities[index])
    if confidence < CONFIDENCE_THRESHOLD:
        return {
            "status": "uncertain",
            "label": None,
            "confidence": confidence,
            "message": "The image is unclear or outside the model's reliable confidence range.",
            "is_healthy": None,
        }
    label = str(classes[index])
    return {
        "status": "prediction",
        "label": label,
        "confidence": confidence,
        "message": "Model prediction for a supported dataset class; confirm with an agricultural expert.",
        "is_healthy": _is_healthy_class(label),
    }
