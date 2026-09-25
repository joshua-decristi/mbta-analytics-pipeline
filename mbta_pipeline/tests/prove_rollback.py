from sqlite3 import Connection
from sqlite3 import IntegrityError as SQLiteIntegrityError

from ..schema import VEHICLE_OBSERVATIONS_TABLE_NAME, create_connection, create_schema
from ..snapshots import load_snapshot

SNAPSHOT = {
    "snapshot_id": "2025-01-01T12:00:00Z",
    "records": [
        {
            "vehicle_id": "0",
            "route_id": "0",
            "latitude": 42.36228,
            "longitude": -71.08701,
            "observed_at": "2024-12-29T12:00:00Z",
        },
        {
            "vehicle_id": "1",
            "route_id": "1",
            "latitude": 42.3503,
            "longitude": -71.0450,
            "observed_at": "2024-12-30T12:00:00Z",
        },
        {
            "vehicle_id": "0",
            "route_id": "0",
            "latitude": 42.3615,
            "longitude": -71.0813,
            "observed_at": "2024-12-31T12:00:00Z",
        },
    ],
}


def get_table_count(connection: Connection):
    cursor = connection.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {VEHICLE_OBSERVATIONS_TABLE_NAME}")
    (count,) = cursor.fetchall()[0]

    print(f"The total count for {VEHICLE_OBSERVATIONS_TABLE_NAME} = {count}")


def main():
    # Setup connection
    print("Setting up temporary SQLite connection")
    connection = create_connection()
    print("\n")

    print("Creating VehicleObservations schema")
    create_schema(connection)
    get_table_count(connection)
    print("\n")

    print("Loading temporary snapshot")
    try:
        load_snapshot(connection, SNAPSHOT["snapshot_id"], SNAPSHOT["records"])

    except SQLiteIntegrityError as error:
        print(f"Caught expected error: {error}")

    finally:
        get_table_count(connection)


main()
