import sqlite3

LOCAL_SQLITE_DB = ":memory:"


def create_connection():
    connection = sqlite3.connect(LOCAL_SQLITE_DB)

    # Enable foreign key support in SQLite (disabled by default)
    connection.cursor().execute("PRAGMA foreign_keys = ON;")

    return connection
