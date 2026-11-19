import pytest

from database.db import create_user, initialize_database, list_records, save_record


def test_database_saves_and_lists_parameterized_records(tmp_path):
    database_path = tmp_path / "test.db"
    initialize_database(database_path)
    user_one = create_user("one@example.test", "hash-one", database_path)
    user_two = create_user("two@example.test", "hash-two", database_path)
    record_id = save_record(
        "soil_reports",
        {"finding": "private"},
        user_id=user_one,
        database_path=database_path,
    )
    records = list_records("soil_reports", user_id=user_one, database_path=database_path)

    assert records[0]["id"] == record_id
    assert records[0]["payload"] == {"finding": "private"}
    assert list_records("soil_reports", user_id=user_two, database_path=database_path) == []


def test_database_rejects_unknown_table(tmp_path):
    with pytest.raises(ValueError, match="Unsupported"):
        save_record(
            "soil_reports; DROP TABLE users",
            {},
            user_id=1,
            database_path=tmp_path / "test.db",
        )
