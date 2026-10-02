"""Tests for app.database."""

from app import database


def use_temp_database(monkeypatch, tmp_path) -> None:
    """Point the module at a fresh database file inside tmp_path."""
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "fruits.db"))


def test_init_db_creates_the_file_and_the_table(monkeypatch, tmp_path):
    use_temp_database(monkeypatch, tmp_path)

    database.init_db()

    assert (tmp_path / "fruits.db").exists()
    with database.get_connection() as connection:
        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(fruits)").fetchall()
        }
    assert columns == {"id", "name", "color", "quantity"}


def test_init_db_can_be_called_repeatedly(monkeypatch, tmp_path):
    use_temp_database(monkeypatch, tmp_path)
    database.init_db()

    database.init_db()

    with database.get_connection() as connection:
        connection.execute(
            "INSERT INTO fruits (name, color, quantity) VALUES ('Kiwi', 'green', 3)"
        )
        count = connection.execute("SELECT COUNT(*) AS total FROM fruits").fetchone()
    assert count["total"] == 1


def test_get_connection_returns_rows_accessible_by_column_name(monkeypatch, tmp_path):
    use_temp_database(monkeypatch, tmp_path)
    database.init_db()

    connection = database.get_connection()
    try:
        connection.execute(
            "INSERT INTO fruits (name, color, quantity) VALUES ('Kiwi', 'green', 3)"
        )
        connection.commit()
        row = connection.execute("SELECT name FROM fruits").fetchone()
    finally:
        connection.close()

    assert row["name"] == "Kiwi"