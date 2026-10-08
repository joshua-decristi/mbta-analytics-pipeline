import json
from dataclasses import dataclass
from typing import Literal, TypedDict

import requests

type VehicleResponse = dict[Literal["data"], list[ResponseVehicle]]

MBTA_URL = "https://api-v3.mbta.com/vehicles?page%5Blimit%5D=1"


class _ResponseVehicleAttributes(TypedDict):
    updated_at: str
    latitude: float
    longitude: float


class _ResponseVehicleRelationshipsRouteData(TypedDict):
    id: str
    type: str


class ResponseVehicle(TypedDict):
    id: str
    type: str
    attributes: _ResponseVehicleAttributes
    relationships: dict[
        Literal["route"], dict[Literal["data"], _ResponseVehicleRelationshipsRouteData]
    ]


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


class VehiclesFromAPIParams(TypedDict):
    src: Literal["API"]


def _vehicles_from_api(params: VehiclesFromAPIParams) -> VehicleResponse:
    print("Fetching from live endpoint")
    response = requests.get(MBTA_URL)
    response.raise_for_status()

    return response.json()


class VehiclesFromFixtureParams(TypedDict):
    src: Literal["FIXTURE"]
    path: str


def _vehicles_from_fixture(params: VehiclesFromFixtureParams) -> VehicleResponse:
    with open(params["path"], "r", encoding="UTF-8") as file:
        return json.load(file)


def get_vehicles(params: VehiclesFromAPIParams | VehiclesFromFixtureParams):
    if params["src"] == "FIXTURE":
        vehicles_response = _vehicles_from_fixture(params)

    else:
        vehicles_response = _vehicles_from_api(params)

    return [Vehicle(vehicle) for vehicle in vehicles_response["data"]]
