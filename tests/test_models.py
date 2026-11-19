import pytest

from services.crop_service import FEATURES, recommend_crops


def test_crop_service_does_not_fake_prediction_without_model(tmp_path):
    values = {
        "N": 90,
        "P": 42,
        "K": 43,
        "temperature": 25,
        "humidity": 70,
        "ph": 6.5,
        "rainfall": 100,
    }

    with pytest.raises(FileNotFoundError, match="not trained"):
        recommend_crops(values, model_path=tmp_path / "missing.joblib")


def test_crop_service_returns_top_three_from_a_trained_model(tmp_path):
    import joblib
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier

    training_values = np.array(
        [
            [90, 40, 40, 20, 50, 6, 100],
            [80, 50, 40, 22, 60, 6.5, 120],
            [70, 60, 50, 25, 70, 7, 150],
            [60, 70, 60, 28, 80, 7.5, 180],
            [50, 80, 70, 30, 85, 8, 200],
            [40, 90, 80, 32, 90, 8.5, 220],
        ],
        dtype=float,
    )
    labels = ["crop-a", "crop-a", "crop-b", "crop-b", "crop-c", "crop-c"]
    model = RandomForestClassifier(n_estimators=10, random_state=1)
    model.fit(training_values, labels)
    model_path = tmp_path / "crop_model.joblib"
    joblib.dump(model, model_path)
    values = dict(zip(FEATURES, training_values[0]))

    result = recommend_crops(values, model_path=model_path)

    assert len(result) == 3
    assert {item["crop"] for item in result} == set(labels)
    assert all(0 <= item["score"] <= 1 for item in result)
    assert sum(item["score"] for item in result) == pytest.approx(1)
