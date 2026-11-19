"""Input validation shared by Streamlit pages and services."""

from numbers import Real


def require_number(name: str, value: object, minimum: float, maximum: float) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a number.")
    number = float(value)
    if not minimum <= number <= maximum:
        raise ValueError(f"{name} must be between {minimum:g} and {maximum:g}.")
    return number


def validate_coordinates(latitude: object, longitude: object) -> tuple[float, float]:
    return (
        require_number("Latitude", latitude, -90, 90),
        require_number("Longitude", longitude, -180, 180),
    )
