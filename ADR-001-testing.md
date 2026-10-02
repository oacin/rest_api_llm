# ADR-001: Testing strategy

- **Status:** Accepted
- **Date:** 2026-10-02

## Context

The Fruit Inventory API is a small CRUD service: five endpoints, one entity, a
single SQLite file. The project must be verifiable quickly by anyone who clones it,
and the exercise brief asks for unit tests only — no separate integration or
end-to-end suite, no CI, no external services.

Something has to be decided here: how do we test a web application without testing the
web server, and how do we keep the tests from touching the developer's real
`fruits.db`?

## Decision

Test the application in-process with **pytest**, using **FastAPI's `TestClient`**
against a **temporary SQLite file**:

- `tests/conftest.py` provides three fixtures:
  - `db_path` points `app.database.DB_PATH` at a file in pytest's `tmp_path`
    directory, so tests never read or write the real database;
  - `client` starts `TestClient(app)` for a fresh, empty database per test;
  - `create_fruit` posts a fruit and returns the created object, to keep the tests
    short.
- The API is driven exactly as a client would drive it — over HTTP semantics, with
  status codes and JSON bodies — but inside the same Python process, without binding
  a port.
- Database creation and the CRUD operations are checked by observing status codes,
  response bodies, and (once) the rows in the SQLite file.
- `simulate.py` covers the "does it work against a real server" question outside the
  test suite; it is run manually, not by pytest.

## Why this approach

- **Fast and hermetic.** No port binding, no server process, no fixtures to install,
  no cleanup beyond `tmp_path`. The whole suite runs in about a second.
- **No risk to local data.** Every test gets its own database file in a temporary
  directory, so a failing or interrupted test run cannot corrupt `fruits.db`.
- **Tests observable behaviour.** Assertions are on status codes, JSON payloads and
  the rows actually written to SQLite, not on internal function calls, so refactoring
  inside `app/` does not break the tests for the wrong reasons.
- **Matches the size of the project.** A separate test suite hierarchy, markers for
  "unit" vs. "integration", or a mocking framework would add more configuration than
  behaviour.

## What is covered

- `GET /fruits`: empty inventory, list of all fruits, ordering by id.
- `GET /fruits/{id}`: found, unknown id (`404`), non-integer id (`422`).
- `POST /fruits`: `201` with an assigned id, whitespace trimming, persistence of the
  new row in the SQLite file.
- `PUT /fruits/{id}`: full replacement, unknown id (`404`), invalid body (`422`) and
  the fruit being left untouched after a rejected update.
- `DELETE /fruits/{id}`: `204` with an empty body, unknown id (`404`), deleting the
  same fruit twice.
- Validation: missing, blank, and over-long `name`, negative and non-integer
  `quantity`.
- `app.database`: the table and file are created automatically, `init_db()` can run
  more than once, rows are addressable by column name.

## What is intentionally not covered

- The real HTTP server (`uvicorn`): process management, ports, shutdown behaviour.
- `simulate.py` itself, since it needs a running server.
- Multiple concurrent clients, performance, and large inventories.
- Anything about deployment, containers, or CI.
- Tests that assert on internal implementation details (SQL strings, helper
  functions), on purpose: they would add maintenance cost without adding confidence.

## Trade-offs

- **Not a true end-to-end test.** `TestClient` skips the network stack, so a problem
  only visible over a real socket (a proxy, a middleware ordering issue) would not be
  caught. `simulate.py` exists as a manual smoke test for that gap.
- **Whole-request tests.** Each test starts up a request and hits a real SQLite file,
  which is slower and heavier than mocking the database, but far more valuable for a
  project this size.
- **One test per behaviour.** The suite is intentionally short; it is a safety net
  for a small API, not a replacement for thought during review.