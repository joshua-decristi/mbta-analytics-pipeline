import json
from argparse import ArgumentParser
from dataclasses import dataclass

from mbta_pipeline.sources import get_vehicles


@dataclass()
class ScriptArgs:
    fixture: str


def _handle_script_args() -> ScriptArgs:
    MBTA_URL_RESPONSE_FIXTURES_FILE = "data/fixtures/raw/vehicles-response.json"

    parser = ArgumentParser(description="Script to trace batch from src")
    parser.add_argument(
        "--fixture",
        type=str,
        default=MBTA_URL_RESPONSE_FIXTURES_FILE,
        help="The path of the fixture file",
    )
    args = parser.parse_args()

    return ScriptArgs(fixture=args.fixture)


def main(fixture: str):
    for vehicle in get_vehicles({"src": "FIXTURE", "path": fixture}):
        print(f"Normalized Vehicle: {vehicle}")


if __name__ == "__main__":
    args = _handle_script_args()

    main(args.fixture)
