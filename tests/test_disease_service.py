import pytest

from services.disease_service import MAX_IMAGE_BYTES, _is_healthy_class, predict_disease


def test_disease_class_health_detection_uses_word_boundaries():
    assert _is_healthy_class("Tomato___healthy")
    assert not _is_healthy_class("Tomato___unhealthy_leaf")


def test_disease_detection_rejects_empty_image():
    with pytest.raises(ValueError, match="empty"):
        predict_disease(b"")


def test_disease_detection_rejects_oversized_image():
    with pytest.raises(ValueError, match="10 MB"):
        predict_disease(b"x" * (MAX_IMAGE_BYTES + 1))
