# Fruit Inventory API

A small CRUD REST API for keeping track of fruits in an inventory, built with
Python, FastAPI and SQLite.

The interesting part of this repository is not the application — it is the **process**.
The whole project, including its specification, tests, architecture decision record and
documentation, was written by an LLM coding agent and then reviewed and verified
step by step. The application itself was deliberately kept as small as possible so
that the result stays easy to read, run and review.

## Features

- Five REST endpoints covering the full CRUD lifecycle of a fruit.
- Automatic validation of the request body with clear `422` responses.
- Correct status codes: `200`, `201`, `204`, `404`, `422`.
- Interactive API documentation at `/docs` (Swagger UI) and `/redoc`.
- Local persistence in a SQLite file that is created automatically — no database
  server, no configuration, no migrations.
- A small, fast unit test suite that never touches the real database.
- `simulate.py`, a script that exercises the running API over HTTP.

## Technology stack

| Layer      | Choice                                              |
| ---------- | --------------------------------------------------- |
| Language   | Python 3.10+                                        |
| Web        | [FastAPI](https://fastapi.tiangolo.com) + Uvicorn    |
| Validation | [Pydantic](https://docs.pydantic.dev) v2            |
| Storage    | SQLite via the standard-library `sqlite3` module    |
| Tests      | [pytest](https://docs.pytest.org) + FastAPI `TestClient` |
| Simulation | [requests](https://requests.readthedocs.io)         |

No other dependencies. No Docker, no frontend, no authentication, no CI.

## Project structure

```text
.
├── app/
│   ├── __init__.py      # package marker
│   ├── main.py          # FastAPI app and the five endpoints
│   ├── database.py      # SQLite connection, schema creation, request dependency
│   └── models.py        # Pydantic models for the request and response bodies
├── tests/
│   ├── conftest.py      # fixtures: temporary database, test client, helper
│   ├── test_database.py # tests for the SQLite layer
│   └── test_fruits.py   # tests for the endpoints
├── SPECIFICATION.md     # what the API must do
├── ADR-001-testing.md   # why the tests are written the way they are
├── simulate.py          # CRUD walkthrough against a running API
├── requirements.txt
└── .gitignore
```

## The fruit entity

| Field      | Type    | Rules                                     |
| ---------- | ------- | ----------------------------------------- |
| `id`       | integer | Assigned by the database, read-only       |
| `name`     | string  | 1–100 characters, required                |
| `color`    | string  | 1–50 characters, required                 |
| `quantity` | integer | `>= 0`, required                          |

`name` and `color` are trimmed of surrounding whitespace before they are validated and
stored, so `"   "` is rejected. Names do not have to be unique.

```json
{ "id": 1, "name": "Apple", "color": "red", "quantity": 12 }
```

## API endpoints

| Method   | Path           | Success | Description                          |
| -------- | -------------- | ------- | ------------------------------------ |
| `GET`    | `/fruits`      | `200`   | List all fruits, ordered by `id`     |
| `GET`    | `/fruits/{id}` | `200`   | Get one fruit                        |
| `POST`   | `/fruits`      | `201`   | Create a fruit                       |
| `PUT`    | `/fruits/{id}` | `200`   | Replace a fruit's fields             |
| `DELETE` | `/fruits/{id}` | `204`   | Delete a fruit (empty body)          |

Errors use FastAPI's standard body:

```json
{ "detail": "Fruit 99 not found" }
```

`422` responses come from Pydantic and list every invalid field.

See [`SPECIFICATION.md`](SPECIFICATION.md) for the complete behaviour contract.

## Getting started

### 1. Install

```bash
git clone <repository-url>
cd rest_api_llm

python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Start the API

```bash
uvicorn app.main:app --reload
```

The API is then available at <http://127.0.0.1:8000>, with interactive documentation at
<http://127.0.0.1:8000/docs>. `fruits.db` is created automatically in the project root
on the first start.

### 3. Try it out

```bash
# Create a fruit
curl -X POST http://127.0.0.1:8000/fruits \
  -H "Content-Type: application/json" \
  -d '{"name": "Apple", "color": "red", "quantity": 12}'

# List all fruits
curl http://127.0.0.1:8000/fruits

# Read one fruit
curl http://127.0.0.1:8000/fruits/1

# Replace it (all writable fields are required)
curl -X PUT http://127.0.0.1:8000/fruits/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Green Apple", "color": "green", "quantity": 8}'

# Delete it
curl -X DELETE http://127.0.0.1:8000/fruits/1

# It is gone
curl -i http://127.0.0.1:8000/fruits/1     # HTTP/1.1 404 Not Found
```

## Running the tests

```bash
pytest
```

The suite is pure `pytest`: every test drives the app in-process with FastAPI's
`TestClient` against a temporary SQLite file in `tmp_path`, so no server is started and
your own `fruits.db` is never touched. (`httpx` in `requirements.txt` is the HTTP client
that `TestClient` builds on.) The reasoning behind this strategy is recorded in
[`ADR-001-testing.md`](ADR-001-testing.md).

## Running the simulation

`simulate.py` performs the full CRUD flow against a **running** API using real HTTP
requests. With the API already running in one terminal, use a second one:

```bash
python simulate.py                          # default: http://127.0.0.1:8000
python simulate.py --url http://127.0.0.1:9000
```

It lists the fruits, creates one, reads it back, updates it, deletes it and confirms it
is gone. Any unexpected status code or unreachable server stops the script with an
error message and a non-zero exit code.

## Database

- Single SQLite file: `fruits.db`, created in the project root on startup.
- One table, created automatically if it does not exist:

  ```sql
  CREATE TABLE IF NOT EXISTS fruits (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      color TEXT NOT NULL,
      quantity INTEGER NOT NULL
  );
  ```

- Data survives restarts. Delete `fruits.db` to start from an empty inventory.
- The file is listed in `.gitignore`, so it never reaches version control.

## Documentation

- [`SPECIFICATION.md`](SPECIFICATION.md) — purpose, scope, entity, endpoints,
  validation, status codes, persistence and testing expectations.
- [`ADR-001-testing.md`](ADR-001-testing.md) — the testing strategy, what it covers,
  what it does not, and why.