"""Exercise a running Fruit Inventory API over HTTP with a full CRUD flow.

Start the API first, then run:

    python simulate.py

The script stops with a non-zero exit code and an explanatory message as soon as a
request fails or the API answers something unexpected.
"""

import argparse
import sys

import requests

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
TIMEOUT_SECONDS = 10


class SimulationError(Exception):
    """Raised when the API cannot be reached or does not behave as specified."""


def request(method: str, url: str, expected_status: int, **kwargs) -> requests.Response:
    """Send a request and fail loudly if the API is unreachable or misbehaves."""
    try:
        response = requests.request(method, url, timeout=TIMEOUT_SECONDS, **kwargs)
    except requests.RequestException as error:
        raise SimulationError(f"could not reach {url} ({error}). Is the API running?") from error

    if response.status_code != expected_status:
        raise SimulationError(
            f"{method} {url} returned HTTP {response.status_code}, "
            f"expected {expected_status}: {response.text}"
        )
    return response


def step(number: int, title: str) -> None:
    print(f"\nStep {number}: {title}")


def show(label: str, value: object) -> None:
    print(f"  {label}: {value}")


def run(base_url: str) -> None:
    print(f"Fruit Inventory API simulation against {base_url}")

    step(1, "List the current fruits")
    fruits = request("GET", f"{base_url}/fruits", expected_status=200).json()
    show("fruits in the inventory", len(fruits))
    for fruit in fruits:
        print(f"    {fruit}")

    step(2, "Create a fruit")
    created = request(
        "POST",
        f"{base_url}/fruits",
        expected_status=201,
        json={"name": "Apple", "color": "red", "quantity": 12},
    ).json()
    fruit_id = created["id"]
    show("created", created)

    step(3, f"Read fruit {fruit_id} back")
    fetched = request("GET", f"{base_url}/fruits/{fruit_id}", expected_status=200).json()
    show("fetched", fetched)
    if fetched != created:
        raise SimulationError(f"fetched fruit {fetched} does not match created fruit {created}")

    step(4, f"Update fruit {fruit_id}")
    updated = request(
        "PUT",
        f"{base_url}/fruits/{fruit_id}",
        expected_status=200,
        json={"name": "Green Apple", "color": "green", "quantity": 8},
    ).json()
    show("updated", updated)

    step(5, f"Delete fruit {fruit_id}")
    response = request("DELETE", f"{base_url}/fruits/{fruit_id}", expected_status=204)
    show("response body", response.text or "<empty>")

    step(6, f"Confirm fruit {fruit_id} is gone")
    request("GET", f"{base_url}/fruits/{fruit_id}", expected_status=404)
    show("result", f"GET /fruits/{fruit_id} returned HTTP 404 as expected")
    remaining = request("GET", f"{base_url}/fruits", expected_status=200).json()
    show("fruits in the inventory", len(remaining))

    print("\nSimulation finished: the full CRUD flow works.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--url",
        default=DEFAULT_BASE_URL,
        help=f"base URL of a running API (default: {DEFAULT_BASE_URL})",
    )
    args = parser.parse_args()

    try:
        run(args.url.rstrip("/"))
    except SimulationError as error:
        print(f"\nFAILED: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())