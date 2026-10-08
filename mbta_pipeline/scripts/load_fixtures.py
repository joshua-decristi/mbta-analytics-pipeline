import json
from argparse import ArgumentParser
from calendar import c
from pathlib import Path
from sqlite3 import Connection
from typing import TypedDict

import duckdb

from ..pipelines import export_vehicle_observations
from ..schema import (
    VEHICLE_OBSERVATIONS_TABLE_NAME,
    VehicleObservationRecord,
    create_connection,
    create_schema,
)
from ..snapshots import VehicleObservationsSnapshot, load_snapshot


def _get_table_count(connection: Connection):
    cursor = connection.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {VEHICLE_OBSERVATIONS_TABLE_NAME}")
    (count,) = cursor.fetchall()[0]

    print(f"The total count for {VEHICLE_OBSERVATIONS_TABLE_NAME} = {count}")


class ScriptArgs(TypedDict):
    fixture: str
    db: str
    parquet: str


def _handle_script_args() -> ScriptArgs:
    parser = ArgumentParser(description="Script to trace batch from src")
    parser.add_argument(
        "--fixture",
        type=str,
        default="data/fixtures/vehicles.json",
        help="The path of the fixture file",
    )
    parser.add_argument(
        "--db",
        type=str,
        default="data/operational/mbta.db",
        help="The path of the SQLite DB file",
    )
    parser.add_argument(
        "--parquet",
        type=str,
        default="data/landing/vehicles/arrival_date=2025-01-01/vehicles.parquet",
        help="The path of the Parquet file",
    )

    args = parser.parse_args()

    return ScriptArgs(fixture=args.fixture, db=args.db, parquet=args.parquet)


def _setup_db(db: str):
    # Setup connection
    print("Setting up SQLite connection")
    Path(db).unlink(missing_ok=True)
    connection = create_connection(db)
    print("\n")

    print("Creating VehicleObservations schema")
    create_schema(connection)
    _get_table_count(connection)
    print("\n")

    return connection


def _load_fixure(fixture: str, connection: Connection):
    print("Loading fixture snapshot")
    with open(fixture, "r", encoding="utf-8") as file:
        snapshot: VehicleObservationsSnapshot = json.load(file)

    load_snapshot(connection, snapshot["snapshot_id"], snapshot["records"])
    _get_table_count(connection)
    print("\n")


def _export_fixture(parquet: str, connection: Connection):
    print("Exporting snapshot to Parquet")
    Path(parquet).unlink(missing_ok=True)
    export_vehicle_observations(connection, parquet)
    print("\n")


def _compare_total(fixture: str, parquet: str, connection: Connection):
    def get_fixture_total():
        with open(fixture, "r", encoding="utf-8") as file:
            snapshot: VehicleObservationsSnapshot = json.load(file)

        return sum([1 for record in snapshot["records"]])

    def get_sqlite_total() -> int:
        cursor = connection.cursor()
        query = f"SELECT COUNT(*) FROM {VEHICLE_OBSERVATIONS_TABLE_NAME}"
        (count,) = cursor.execute(query).fetchone() or (0,)

        return count

    def get_parquet_total():
        query = f"""
            SELECT COUNT(*) AS total
            FROM read_parquet('{parquet}');
        """

        (count,) = duckdb.query(query).fetchone() or (0,)
        return count

    fixture_count = get_fixture_total()
    sqlite_count = get_sqlite_total()
    parquet_count = get_parquet_total()

    if not fixture_count == sqlite_count == parquet_count:
        raise Exception("Fixture Count, SQLite Count, & Parquet Count are not same")

    print(
        f"Fixture Count: {fixture_count}, "
        + f"SQLite Count: {sqlite_count}, "
        + f"Parquet Count: {parquet_count}"
    )


def _compare_single_record(
    fixture: str,
    parquet: str,
    connection: Connection,
):
    def get_from_fixture() -> VehicleObservationRecord:
        with open(fixture, "r", encoding="utf-8") as file:
            snapshot: VehicleObservationsSnapshot = json.load(file)

        return {"snapshot_id": snapshot["snapshot_id"], **snapshot["records"][0]}

    def get_from_sqlite(
        snapshot_id: str, vehicle_id: str
    ) -> VehicleObservationRecord | None:
        cursor = connection.cursor()
        query = f"""
            SELECT *
            FROM {VEHICLE_OBSERVATIONS_TABLE_NAME}
            WHERE snapshot_id = ?
              AND vehicle_id = ?
        """
        row = cursor.execute(query, (snapshot_id, vehicle_id)).fetchone()

        if not row:
            return None

        return {
            "snapshot_id": row[0],
            "vehicle_id": row[1],
            "route_id": row[2],
            "latitude": row[3],
            "longitude": row[4],
            "observed_at": row[5],
        }

    def get_from_parquet(
        snapshot_id: str, vehicle_id: str
    ) -> VehicleObservationRecord | None:
        query = f"""
            SELECT *
            FROM read_parquet('{parquet}')
            WHERE snapshot_id = '{snapshot_id}'
              AND vehicle_id = '{vehicle_id}';
        """

        row = duckdb.query(query).fetchone()

        if not row:
            return None

        return {
            "snapshot_id": row[0],
            "vehicle_id": row[1],
            "route_id": row[2],
            "latitude": row[3],
            "longitude": row[4],
            "observed_at": row[5],
        }

    fixture_vehicle_observation = get_from_fixture()
    sqlite_vehicle_observation = get_from_sqlite(
        fixture_vehicle_observation["snapshot_id"],
        fixture_vehicle_observation["vehicle_id"],
    )
    parquet_vehicle_observation = get_from_parquet(
        fixture_vehicle_observation["snapshot_id"],
        fixture_vehicle_observation["vehicle_id"],
    )

    all_same = (
        fixture_vehicle_observation
        == sqlite_vehicle_observation
        == parquet_vehicle_observation
    )
    if not all_same:
        raise Exception(
            "Fixture Record, SQLite Record, & Parquet Record not have same values"
        )

    print(
        f"Snapshot Id: {fixture_vehicle_observation['snapshot_id']}, "
        + f"Vehicle Id: {fixture_vehicle_observation['vehicle_id']}, "
    )
    print(f"Storage Locations have same record: {all_same}")


def main(fixture: str, db: str, parquet: str):
    connection = _setup_db(db)
    _load_fixure(fixture, connection)
    _export_fixture(parquet, connection)
    _compare_total(fixture, parquet, connection)
    _compare_single_record(fixture, parquet, connection)


if __name__ == "__main__":
    args = _handle_script_args()

    main(**args)
