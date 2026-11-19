import pytest

from database.db import initialize_database
from services.auth_service import (
    MAX_LOGIN_ATTEMPTS,
    authenticate_user,
    hash_password,
    normalize_email,
    register_user,
    verify_password,
)


def test_password_hash_is_salted_and_verifies_password():
    first = hash_password("a-long-test-passphrase")
    second = hash_password("a-long-test-passphrase")

    assert first != second
    assert verify_password("a-long-test-passphrase", first)
    assert not verify_password("wrong-passphrase", first)


def test_password_requires_minimum_length():
    with pytest.raises(ValueError, match="at least|12"):
        hash_password("short")


def test_registration_and_login_normalize_email(tmp_path):
    database_path = tmp_path / "auth.db"
    initialize_database(database_path)
    registered = register_user(
        "Farmer@Example.test",
        "correct-horse-battery",
        database_path,
    )

    authenticated, error = authenticate_user(
        " farmer@example.test ",
        "correct-horse-battery",
        database_path=database_path,
    )

    assert error is None
    assert authenticated == registered


def test_login_rate_limit_blocks_repeated_bad_passwords(tmp_path):
    database_path = tmp_path / "auth.db"
    initialize_database(database_path)
    register_user("farmer@example.test", "correct-horse-battery", database_path)
    result = None

    for attempt in range(MAX_LOGIN_ATTEMPTS):
        result = authenticate_user(
            "farmer@example.test",
            "incorrect-password",
            now=1000 + attempt,
            database_path=database_path,
        )

    assert result is not None
    assert result[0] is None
    assert "Too many" in result[1]
    blocked, error = authenticate_user(
        "farmer@example.test",
        "correct-horse-battery",
        now=1006,
        database_path=database_path,
    )
    assert blocked is None
    assert "Too many" in error


def test_invalid_email_is_rejected():
    with pytest.raises(ValueError, match="valid email"):
        normalize_email("not-an-email")
