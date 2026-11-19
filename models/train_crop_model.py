"""Train the crop classifier from datasets/crop_recommendation/Crop_recommendation.csv."""

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

from config import PROJECT_ROOT, TRAINED_MODELS_DIR
from services.crop_service import FEATURES

DATASET = PROJECT_ROOT / "datasets" / "crop_recommendation" / "Crop_recommendation.csv"
TARGET = "label"


def train(dataset_path: Path = DATASET) -> dict:
    if not dataset_path.is_file():
        raise FileNotFoundError(
            f"Dataset not found at {dataset_path}. Add a documented public crop dataset CSV."
        )
    data = pd.read_csv(dataset_path)
    missing = set(FEATURES + [TARGET]) - set(data.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(sorted(missing))}")
    data = data[FEATURES + [TARGET]].dropna()
    if data[TARGET].nunique() < 2:
        raise ValueError("Training requires at least two crop classes.")
    counts = data[TARGET].value_counts()
    stratify = data[TARGET] if counts.min() >= 2 else None
    x_train, x_test, y_train, y_test = train_test_split(
        data[FEATURES],
        data[TARGET].astype(str),
        test_size=0.2,
        random_state=42,
        stratify=stratify,
    )
    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
    )
    model.fit(x_train.to_numpy(), y_train)
    predictions = model.predict(x_test.to_numpy())
    metrics = {
        "test_accuracy": float(accuracy_score(y_test, predictions)),
        "test_samples": int(len(y_test)),
        "classification_report": classification_report(
            y_test, predictions, output_dict=True, zero_division=0
        ),
        "dataset": str(dataset_path.relative_to(PROJECT_ROOT)),
        "split": "80% train / 20% test; random_state=42",
    }
    TRAINED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, TRAINED_MODELS_DIR / "crop_model.joblib")
    (TRAINED_MODELS_DIR / "crop_metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )
    return metrics


if __name__ == "__main__":
    print(json.dumps(train(), indent=2))
