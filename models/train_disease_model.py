"""Train MobileNetV2 on datasets/plant_disease/{train,test}/<class>/ images."""

import json
from pathlib import Path

from config import PROJECT_ROOT, TRAINED_MODELS_DIR

DATASET_DIR = PROJECT_ROOT / "datasets" / "plant_disease"
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
SEED = 42


def train(dataset_dir: Path = DATASET_DIR, epochs: int = 5) -> dict:
    try:
        import tensorflow as tf
    except ImportError as exc:
        raise RuntimeError("Install the optional TensorFlow dependency to train the image model.") from exc
    train_dir = dataset_dir / "train"
    test_dir = dataset_dir / "test"
    if not train_dir.is_dir() or not test_dir.is_dir():
        raise FileNotFoundError(
            f"Expected separate train and test image folders under {dataset_dir}."
        )
    train_ds = tf.keras.utils.image_dataset_from_directory(
        train_dir,
        validation_split=0.2,
        subset="training",
        seed=SEED,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
    )
    validation_ds = tf.keras.utils.image_dataset_from_directory(
        train_dir,
        validation_split=0.2,
        subset="validation",
        seed=SEED,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
    )
    test_ds = tf.keras.utils.image_dataset_from_directory(
        test_dir,
        shuffle=False,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
    )
    classes = train_ds.class_names
    if len(classes) < 2 or test_ds.class_names != classes:
        raise ValueError("Train and test folders must contain the same two or more class names.")
    autotune = tf.data.AUTOTUNE
    train_ds = train_ds.prefetch(autotune)
    validation_ds = validation_ds.prefetch(autotune)
    test_ds = test_ds.prefetch(autotune)

    base = tf.keras.applications.MobileNetV2(
        input_shape=(*IMAGE_SIZE, 3), include_top=False, weights="imagenet"
    )
    base.trainable = False
    inputs = tf.keras.Input(shape=(*IMAGE_SIZE, 3))
    x = tf.keras.applications.mobilenet_v2.preprocess_input(inputs)
    x = base(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    outputs = tf.keras.layers.Dense(len(classes), activation="softmax")(x)
    model = tf.keras.Model(inputs, outputs)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.fit(train_ds, validation_data=validation_ds, epochs=epochs)
    test_loss, test_accuracy = model.evaluate(test_ds, verbose=0)

    TRAINED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model.save(TRAINED_MODELS_DIR / "disease_model.keras")
    (TRAINED_MODELS_DIR / "disease_classes.json").write_text(
        json.dumps(classes, indent=2), encoding="utf-8"
    )
    test_samples = sum(int(labels.shape[0]) for _, labels in test_ds)
    metrics = {
        "test_loss": float(test_loss),
        "test_accuracy": float(test_accuracy),
        "test_samples": test_samples,
        "class_names": classes,
        "dataset": str(dataset_dir.relative_to(PROJECT_ROOT)),
        "split": "train folder split 80/20 for training/validation; separate test folder",
    }
    (TRAINED_MODELS_DIR / "disease_metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )
    return metrics


if __name__ == "__main__":
    print(json.dumps(train(), indent=2))
