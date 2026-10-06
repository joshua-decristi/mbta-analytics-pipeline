import os
from sqlite3 import Connection

import pyarrow as pa
import pyarrow.parquet as pq

from ..schema import VEHICLE_OBSERVATIONS_TABLE_NAME, VehicleObservationRecord


def _fetch_vehicle_observations(connection: Connection):
    query = f"""
        SELECT *
        FROM {VEHICLE_OBSERVATIONS_TABLE_NAME}
        ORDER BY snapshot_id ASC, vehicle_id ASC
    """

    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    vehicle_observations: list[VehicleObservationRecord] = [
        {
            "snapshot_id": row[0],
            "vehicle_id": row[1],
            "route_id": row[2],
            "latitude": row[3],
            "longitude": row[4],
            "observed_at": row[5],
        }
        for row in rows
    ]

    return vehicle_observations


def _write_table(table, parquet_location: str):
    dir_path = os.path.dirname(parquet_location)
    os.makedirs(dir_path, exist_ok=True)

    pq.write_table(table, parquet_location, compression="zstd")


def export_vehicle_observations(connection: Connection):
    # Fetch vehicles from OLTP
    vehicle_observations = _fetch_vehicle_observations(connection)

    # Convert to columnart Table
    table = pa.Table.from_pylist(vehicle_observations)

    # Write table to parquet
    _write_table(
        table, "data/landing/vehicles/arrival_date=2025-01-01/vehicles.parquet"
    )
