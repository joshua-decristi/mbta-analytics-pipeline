import sqlite3

LOCAL_SQLITE_DB = ":memory:"


def create_connection(db_path: str = LOCAL_SQLITE_DB):
    connection = sqlite3.connect(db_path)

    # Enable foreign key support in SQLite (disabled by default)
    connection.cursor().execute("PRAGMA foreign_keys = ON;")

    return connection
