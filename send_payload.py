import json
from requests import Session
from typing import Any

from argparse import ArgumentParser


SERVER_HOST = "127.0.0.1"
SERVER_PORT = "8888"


def load_data(filename: str) -> dict[str, Any]:
    with open(filename, "r") as file:
        content = file.read()
    return json.loads(content)


def get_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument("filename", type=str, help="Payload filename")

    return parser


def main() -> None:
    # Parse args
    parser = get_parser()
    args = parser.parse_args()

    # Load data file
    data = load_data(args.filename)

    session = Session()
    resp = session.post(f"http://{SERVER_HOST}:{SERVER_PORT}/productionplan", json=data)

    if resp.status_code == 200:
        print("Found solution for powerplants loads:")
        total_production = 0.0
        for item in resp.json():
            print("  - ", item["name"], item["p"])
            total_production += item["p"]
        print("\nTotal Production :", total_production)

    else:
        print("Response status", resp.status_code)
        print("Response content", resp.text)


if __name__ == "__main__":
    main()
