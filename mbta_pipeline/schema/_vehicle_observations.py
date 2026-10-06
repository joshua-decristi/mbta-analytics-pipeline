from sqlite3 import Cursor
from typing import TypedDict

VEHICLE_OBSERVATIONS_TABLE_NAME = "vehicle_observations"


class VehicleObservationRecord(TypedDict):
    snapshot_id: str
    vehicle_id: str
    route_id: str
    latitude: float
    longitude: float
    observed_at: str


# Create Vehicle Observations table
def create_vehicle_observations_schema(connection_cursor: Cursor):
    connection_cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {VEHICLE_OBSERVATIONS_TABLE_NAME} (
            snapshot_id TEXT CHECK (datetime(snapshot_id) IS NOT NULL),
            vehicle_id TEXT NOT NULL,
            route_id TEXT NOT NULL,
            latitude DOUBLE NOT NULL,
            longitude DOUBLE NOT NULL,
            observed_at TEXT CHECK (datetime(observed_at) IS NOT NULL),

            -- Defining the composite primary key
            PRIMARY KEY (snapshot_id, vehicle_id)
        );
    """)
