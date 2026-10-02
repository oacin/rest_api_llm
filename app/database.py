"""SQLite access: connection handling, schema creation, request dependency."""

import sqlite3

DB_PATH = "fruits.db"

CREATE_FRUITS_TABLE = """
CREATE TABLE IF NOT EXISTS fruits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    color TEXT NOT NULL,
    quantity INTEGER NOT NULL
)
"""


def get_connection() -> sqlite3.Connection:
    """Open a connection to the SQLite database, rows accessible by column name."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    """Create the database file and the fruits table if they do not exist yet."""
    with get_connection() as connection:
        connection.execute(CREATE_FRUITS_TABLE)


def get_db():
    """FastAPI dependency: yield a connection, commit on success, always close."""
    connection = get_connection()
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()