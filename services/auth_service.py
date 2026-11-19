"""Local account authentication using salted PBKDF2 password hashes."""

import hashlib
import hmac
import re
import secrets
import sqlite3
import time
from pathlib import Path

from database.db import (
    clear_login_attempts,
    create_user,
    get_login_attempt,
    get_user_by_email,
    record_login_failure,
)
from config import DATABASE_PATH

HASH_ALGORITHM = "pbkdf2_sha256"
HASH_ITERATIONS = 600_000
SALT_BYTES = 16
MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 1024
LOGIN_WINDOW_SECONDS = 15 * 60
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 15 * 60
EMAIL_PATTERN = re.compile(r"^[^@\s]{1,64}@[^@\s.]+(?:\.[^@\s.]+)+$")
DUMMY_PASSWORD_HASH = (
    f"{HASH_ALGORITHM}${HASH_ITERATIONS}${bytes(SALT_BYTES).hex()}${bytes(32).hex()}"
)


def normalize_email(email: str) -> str:
    normalized = email.strip().casefold()
    if len(normalized) > 254 or not EMAIL_PATTERN.fullmatch(normalized):
        raise ValueError("Enter a valid email address.")
    return normalized


def hash_password(password: str) -> str:
    if not MIN_PASSWORD_LENGTH <= len(password) <= MAX_PASSWORD_LENGTH:
        raise ValueError(
            f"Password must contain {MIN_PASSWORD_LENGTH} to {MAX_PASSWORD_LENGTH} characters."
        )
    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, HASH_ITERATIONS
    )
    return f"{HASH_ALGORITHM}${HASH_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded_hash: str) -> bool:
    try:
        algorithm, iterations, salt_hex, digest_hex = encoded_hash.split("$")
        if algorithm != HASH_ALGORITHM:
            return False
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.pbkdf2_hmac(
            algorithm.removeprefix("pbkdf2_"),
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations),
        )
    except (ValueError, TypeError, UnicodeEncodeError):
        return False
    return hmac.compare_digest(actual, expected)


def register_user(
    email: str,
    password: str,
    database_path: Path = DATABASE_PATH,
) -> dict[str, int | str]:
    normalized_email = normalize_email(email)
    password_hash = hash_password(password)
    try:
        user_id = create_user(normalized_email, password_hash, database_path)
    except sqlite3.IntegrityError as exc:
        raise ValueError("An account with this email already exists.") from exc
    return {"id": user_id, "email": normalized_email}


def authenticate_user(
    email: str,
    password: str,
    now: int | None = None,
    database_path: Path = DATABASE_PATH,
) -> tuple[dict[str, int | str] | None, str | None]:
    normalized_email = normalize_email(email)
    current_time = int(time.time()) if now is None else now
    attempt = get_login_attempt(normalized_email, database_path)
    if attempt and attempt["locked_until"] and current_time < attempt["locked_until"]:
        return None, "Too many failed sign-in attempts. Try again in 15 minutes."

    user = get_user_by_email(normalized_email, database_path)
    password_matches = verify_password(
        password,
        user["password_hash"] if user else DUMMY_PASSWORD_HASH,
    ) and user is not None
    if not password_matches:
        count = record_login_failure(
            normalized_email,
            current_time,
            LOGIN_WINDOW_SECONDS,
            MAX_LOGIN_ATTEMPTS,
            LOCKOUT_SECONDS,
            database_path,
        )
        if count >= MAX_LOGIN_ATTEMPTS:
            return None, "Too many failed sign-in attempts. Try again in 15 minutes."
        return None, "Email or password is incorrect."

    clear_login_attempts(normalized_email, database_path)
    return {"id": int(user["id"]), "email": str(user["email"])}, None
