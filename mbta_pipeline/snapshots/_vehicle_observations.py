from sqlite3 import Connection
from sqlite3 import Error as SQLiteError
from typing import TypedDict

from ..schema import VEHICLE_OBSERVATIONS_TABLE_NAME

type VehicleObservationRecord = list[tuple[str, str, str, float, float, str]]


class VehicleObservationsSnapshotRecord(TypedDict):
    vehicle_id: str
    route_id: str
    latitude: float
    longitude: float
    observed_at: str


class VehicleObservationsSnapshot(TypedDict):
    snapshot_id: str
    records: list[VehicleObservationsSnapshotRecord]


# Load Vehicle Observations from snapshot
def load_vehicle_response_snapshot(
    connection: Connection,
    snapshot_id: str,
    observations: list[VehicleObservationsSnapshotRecord],
):
    print(f'Inserting snapshot: "{snapshot_id}" into SQLite')
    cursor = connection.cursor()

    sql = f"""
      INSERT INTO {VEHICLE_OBSERVATIONS_TABLE_NAME} (snapshot_id, vehicle_id, route_id, latitude, longitude, observed_at)
      VALUES ( ?, ?, ?, ?, ?, ? )
    """

    try:
        records: VehicleObservationRecord = [
            (
                snapshot_id,
                record["vehicle_id"],
                record["route_id"],
                record["latitude"],
                record["longitude"],
                record["observed_at"],
            )
            for record in observations
        ]

        cursor.executemany(sql, records)
        connection.commit()
        print(f"Successfully inserted {len(observations)} snapshot into SQLite")

    except SQLiteError:
        print(f'Failed to insert snapshot: "{snapshot_id}" into SQLite')
        connection.rollback()
        raise
