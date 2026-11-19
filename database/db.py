"""Small parameterized SQLite helpers for module history."""

import json
import sqlite3
from pathlib import Path
from typing import Any

from config import DATABASE_PATH, PROJECT_ROOT

RECORD_TABLES = {
    "soil_reports",
    "crop_recommendations",
    "disease_detections",
    "weather_records",
    "irrigation_records",
    "risk_assessments",
    "ai_conversations",
}


def get_connection(database_path: Path = DATABASE_PATH) -> sqlite3.Connection:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout = 5000")
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(database_path: Path = DATABASE_PATH) -> None:
    schema_path = PROJECT_ROOT / "database" / "schema.sql"
    with get_connection(database_path) as connection:
        connection.executescript(schema_path.read_text(encoding="utf-8"))


def save_record(
    table: str,
    payload: dict[str, Any],
    user_id: int,
    farm_id: int | None = None,
    database_path: Path = DATABASE_PATH,
) -> int:
    if table not in RECORD_TABLES:
        raise ValueError("Unsupported history table.")
    if isinstance(user_id, bool) or not isinstance(user_id, int) or user_id < 1:
        raise ValueError("A valid user ID is required to save a record.")
    serialized = json.dumps(payload, ensure_ascii=False, allow_nan=False)
    with get_connection(database_path) as connection:
        cursor = connection.execute(
            f"INSERT INTO {table} (user_id, farm_id, payload_json) VALUES (?, ?, ?)",
            (user_id, farm_id, serialized),
        )
        return int(cursor.lastrowid)


def list_records(
    table: str,
    user_id: int,
    limit: int = 100,
    database_path: Path = DATABASE_PATH,
) -> list[dict[str, Any]]:
    if table not in RECORD_TABLES:
        raise ValueError("Unsupported history table.")
    if isinstance(user_id, bool) or not isinstance(user_id, int) or user_id < 1:
        raise ValueError("A valid user ID is required to read records.")
    if not 1 <= limit <= 1000:
        raise ValueError("History limit must be between 1 and 1000.")
    with get_connection(database_path) as connection:
        rows = connection.execute(
            f"SELECT id, payload_json, created_at FROM {table} "
            "WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    return [
        {"id": row["id"], "created_at": row["created_at"], "payload": json.loads(row["payload_json"])}
        for row in rows
    ]


def create_user(email: str, password_hash: str, database_path: Path = DATABASE_PATH) -> int:
    with get_connection(database_path) as connection:
        cursor = connection.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (email, password_hash),
        )
        return int(cursor.lastrowid)


def get_user_by_email(email: str, database_path: Path = DATABASE_PATH) -> dict[str, Any] | None:
    with get_connection(database_path) as connection:
        row = connection.execute(
            "SELECT id, email, password_hash FROM users WHERE email = ?",
            (email,),
        ).fetchone()
    return dict(row) if row else None


def get_login_attempt(email: str, database_path: Path = DATABASE_PATH) -> dict[str, Any] | None:
    with get_connection(database_path) as connection:
        row = connection.execute(
            "SELECT failed_count, window_started_at, locked_until "
            "FROM login_attempts WHERE email = ?",
            (email,),
        ).fetchone()
    return dict(row) if row else None


def record_login_failure(
    email: str,
    now: int,
    window_seconds: int,
    max_attempts: int,
    lockout_seconds: int,
    database_path: Path = DATABASE_PATH,
) -> int:
    with get_connection(database_path) as connection:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "DELETE FROM login_attempts WHERE window_started_at < ?",
            (now - window_seconds * 24,),
        )
        row = connection.execute(
            "SELECT failed_count, window_started_at FROM login_attempts WHERE email = ?",
            (email,),
        ).fetchone()
        if row is None or now - row["window_started_at"] >= window_seconds:
            count = 1
            window_started = now
        else:
            count = int(row["failed_count"]) + 1
            window_started = int(row["window_started_at"])
        locked_until = now + lockout_seconds if count >= max_attempts else None
        connection.execute(
            """
            INSERT INTO login_attempts (email, failed_count, window_started_at, locked_until)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET
                failed_count = excluded.failed_count,
                window_started_at = excluded.window_started_at,
                locked_until = excluded.locked_until
            """,
            (email, count, window_started, locked_until),
        )
    return count


def clear_login_attempts(email: str, database_path: Path = DATABASE_PATH) -> None:
    with get_connection(database_path) as connection:
        connection.execute("DELETE FROM login_attempts WHERE email = ?", (email,))
