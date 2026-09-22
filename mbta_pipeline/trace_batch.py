import json
from dataclasses import dataclass
from typing import Literal, TypedDict

import requests

with open("data/fixtures/vehicles.json", "r", encoding="utf-8") as file:
    vehicles = json.load(file)

print(f"snapshot_id: {vehicles['snapshot_id']}")
print(f"record_count: {len(vehicles['records'])}")
print(f"sorted: {sorted(vehicles['records'][0])}")


## Normalize Vehicles

MBTA_URL = "https://api-v3.mbta.com/vehicles?page%5Blimit%5D=1"
MBTA_URL_RESPONSE_FIXTURES_FILE = "data/fixtures/raw/vehicles-response.json"


class ResponseVehicleAttributes(TypedDict):
    updated_at: str
    latitude: float
    longitude: float


class ResponseVehicleRelationshipsRouteData(TypedDict):
    id: str
    type: str


class ResponseVehicle(TypedDict):
    id: str
    type: str
    attributes: ResponseVehicleAttributes
    relationships: dict[
        Literal["route"], dict[Literal["data"], ResponseVehicleRelationshipsRouteData]
    ]


response_vehicles: dict[Literal["data"], list[ResponseVehicle]] = {}


@dataclass
class Vehicle:
    vehicle_id: str
    route_id: str
    latitude: float
    longitude: float
    observed_at: str

    def __init__(self, response: ResponseVehicle):
        self.vehicle_id = response["id"]
        self.route_id = response["relationships"]["route"]["data"]["id"]
        self.latitude = response["attributes"]["latitude"]
        self.longitude = response["attributes"]["longitude"]
        self.observed_at = response["attributes"]["updated_at"]


try:
    print("Fetching from live endpoint")
    response = requests.get(MBTA_URL)
    response.raise_for_status()

    response_vehicles = response.json()

except requests.exceptions.RequestException:
    print("Live endpoint failed, using fixture as backup")

    with open(MBTA_URL_RESPONSE_FIXTURES_FILE, "r", encoding="UTF-8") as file:
        response_vehicles = json.load(file)


for response_vehicle in response_vehicles["data"]:
    print(f"Normalized Vehicle: {Vehicle(response_vehicle)}")
