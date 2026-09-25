import json

import duckdb

from ..schema import VEHICLE_OBSERVATIONS_TABLE_NAME, create_connection
from ..snapshots import VehicleObservationsSnapshot

PARQUET_PATH = "data/landing/vehicles/arrival_date=2025-01-01/vehicles.parquet"
SQLITE_DB_PATH = "data/operational/mbta.db"
JSON_FIXTURES_PATH = "data/fixtures/vehicles.json"


def _ensure_get_count_by_route_is_correct():
    def get_count_by_route():
        query = f"""
            SELECT route_id, COUNT(*) AS route_count
            FROM read_parquet('{PARQUET_PATH}')
            GROUP BY route_id
            ORDER BY route_id;
        """
        response = duckdb.query(query)
        print("Counts by Route: ")
        print(response)

        return response.fetchall()

    def get_total():
        query = f"""
            SELECT COUNT(*) AS total
            FROM read_parquet('{PARQUET_PATH}');
        """

        (count,) = duckdb.query(query).fetchone() or (0,)
        return count

    counts_by_route = get_count_by_route()
    total = get_total()

    print(f"Total: {total}")
    print(f"Counts Sum = Total: {sum(count[1] for count in counts_by_route) == total}")


def _compare_data_sources(vehicle_id: str):
    def get_from_sqlite() -> int:
        connection = create_connection(SQLITE_DB_PATH)
        cursor = connection.cursor()
        query = f"SELECT COUNT(*) FROM {VEHICLE_OBSERVATIONS_TABLE_NAME} WHERE vehicle_id = ?"
        (count,) = cursor.execute(query, (vehicle_id,)).fetchall()[0]

        return count

    def get_from_json() -> int:
        with open(JSON_FIXTURES_PATH, "r", encoding="utf-8") as file:
            snapshot: VehicleObservationsSnapshot = json.load(file)

        return sum(
            [1 for record in snapshot["records"] if record["vehicle_id"] == vehicle_id]
        )

    def get_from_parquet() -> int:
        query = f"""
            SELECT COUNT(*) AS total
            FROM read_parquet('{PARQUET_PATH}')
            WHERE vehicle_id = {vehicle_id};
        """

        (count,) = duckdb.query(query).fetchone() or (0,)
        return count

    print(f"Vehicle Id: {vehicle_id}")
    print(f"Count from SQLite: {get_from_sqlite()}")
    print(f"Count from JSON: {get_from_json()}")
    print(f"Count from Parquet: {get_from_parquet()}")


def main():
    _ensure_get_count_by_route_is_correct()
    print("\n")

    _compare_data_sources("0")


main()
