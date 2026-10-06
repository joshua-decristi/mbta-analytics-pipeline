import json
from sqlite3 import Connection
from sqlite3 import IntegrityError as SQLiteIntegrityError

from ..pipelines import export_vehicle_observations
from ..schema import VEHICLE_OBSERVATIONS_TABLE_NAME, create_connection, create_schema
from ..snapshots import VehicleObservationsSnapshot, load_snapshot

SQLITE_DB_PATH = "data/operational/mbta.db"
JSON_FIXTURES_PATH = "data/fixtures/vehicles.json"

with open(JSON_FIXTURES_PATH, "r", encoding="utf-8") as file:
    snapshot: VehicleObservationsSnapshot = json.load(file)


def get_table_count(connection: Connection):
    cursor = connection.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {VEHICLE_OBSERVATIONS_TABLE_NAME}")
    (count,) = cursor.fetchall()[0]

    print(f"The total count for {VEHICLE_OBSERVATIONS_TABLE_NAME} = {count}")


def main():
    # Setup connection
    print("Setting up temporary SQLite connection")
    connection = create_connection(SQLITE_DB_PATH)
    print("\n")

    print("Creating VehicleObservations schema")
    create_schema(connection)
    get_table_count(connection)
    print("\n")

    print("Loading temporary snapshot")
    try:
        load_snapshot(connection, snapshot["snapshot_id"], snapshot["records"])
        export_vehicle_observations(connection)

    except SQLiteIntegrityError as error:
        print(f"Caught expected error: {error}")

    finally:
        get_table_count(connection)


main()
