from sqlite3 import Cursor

VEHICLE_OBSERVATIONS_TABLE_NAME = "vehicle_observations"


# Create Vehicle Observations table
def create_vehicle_observations_schema(connection_cursor: Cursor):
    connection_cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {VEHICLE_OBSERVATIONS_TABLE_NAME} (
            snapshot_id TEXT NOT NULL,
            vehicle_id TEXT NOT NULL,
            route_id TEXT NOT NULL,
            latitude DOUBLE NOT NULL,
            longitude DOUBLE NOT NULL,
            observed_at TEXT NOT NULL,

            -- Defining the composite primary key
            PRIMARY KEY (snapshot_id, vehicle_id)
        );
    """)
