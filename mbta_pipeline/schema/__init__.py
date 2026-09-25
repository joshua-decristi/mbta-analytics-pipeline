from sqlite3 import Connection

from ._sqlite import create_connection
from ._vehicle_observations import (
    VEHICLE_OBSERVATIONS_TABLE_NAME,
    VehicleObservationRecord,
)
from ._vehicle_observations import (
    create_vehicle_observations_schema as _create_vehicle_observations_schema,
)


def create_schema(connection: Connection):
    cursor = connection.cursor()

    # Create Vehicle Observations table
    _create_vehicle_observations_schema(cursor)

    # Create other tables below
    # ...


# Expose create_connection function at the module root
__all__ = [
    "VEHICLE_OBSERVATIONS_TABLE_NAME",
    "VehicleObservationRecord",
    "create_connection",
]
