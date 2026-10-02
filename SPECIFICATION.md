# Specification — Fruit Inventory REST API

## 1. Purpose

A small REST API that keeps track of fruits in an inventory. It exists as a hands-on
exercise in building a complete project with an LLM coding agent, so it is
deliberately minimal: one entity, five endpoints, local file persistence.

## 2. Scope

In scope:

- Create, read, update and delete fruits.
- Persist fruits in a local SQLite file that is created automatically.
- Validate input and return meaningful HTTP status codes.

Out of scope:

- Authentication, authorisation, users, roles.
- Pagination, filtering, sorting, search.
- Frontend, deployment, containers, migrations, external database servers.
- Concurrency control, auditing, versioning of the payload format.

## 3. Domain entity

One entity: **Fruit**.

| Field     | Type    | Required | Rules                                    |
| --------- | ------- | -------- | ---------------------------------------- |
| `id`      | integer | yes      | Assigned by the database, read-only      |
| `name`    | string  | yes      | 1–100 characters after trimming          |
| `color`   | string  | yes      | 1–50 characters after trimming           |
| `quantity`| integer | yes      | Whole number, `>= 0`                     |

Additional rules:

- `name` and `color` are stripped of leading/trailing whitespace before validation
  and storage. A value that is empty after stripping (or only whitespace) is invalid.
- Names do not have to be unique. No other business rules are enforced.
- A fruit is never partially updated: `PUT` replaces `name`, `color` and `quantity`.

Example fruit:

```json
{ "id": 1, "name": "Apple", "color": "red", "quantity": 12 }
```

## 4. API

Base path: `/fruits`. All requests and responses use JSON.

| Method   | Path            | Success | Description                             |
| -------- | --------------- | ------- | --------------------------------------- |
| `GET`    | `/fruits`       | `200`   | List all fruits, ordered by `id`        |
| `GET`    | `/fruits/{id}`  | `200`   | Get a single fruit                      |
| `POST`   | `/fruits`       | `201`   | Create a fruit                          |
| `PUT`    | `/fruits/{id}`  | `200`   | Replace a fruit                         |
| `DELETE` | `/fruits/{id}`  | `204`   | Delete a fruit (empty response body)    |

The framework additionally serves interactive documentation at `/docs` and `/redoc`.

### 4.1 `GET /fruits`

Request body: none.

Response `200`:

```json
[{ "id": 1, "name": "Apple", "color": "red", "quantity": 12 }]
```

An empty inventory returns `200` with an empty array.

### 4.2 `GET /fruits/{id}`

Response `200`: the fruit object. Unknown `id` returns `404`.

### 4.3 `POST /fruits`

Request body — all fields required:

```json
{ "name": "Apple", "color": "red", "quantity": 12 }
```

Response `201` — the stored fruit, including the assigned `id`:

```json
{ "id": 1, "name": "Apple", "color": "red", "quantity": 12 }
```

### 4.4 `PUT /fruits/{id}`

Request body has exactly the same shape as `POST /fruits`. Response `200` returns the
updated fruit. Unknown `id` returns `404` and nothing is modified.

### 4.5 `DELETE /fruits/{id}`

Response `204` with an empty body. Unknown `id` returns `404` and nothing is deleted.
Deleting an already deleted fruit therefore returns `404`.

## 5. Status codes

| Code  | When                                                            |
| ----- | --------------------------------------------------------------- |
| `200` | Successful read or update                                       |
| `201` | Fruit created                                                   |
| `204` | Fruit deleted                                                   |
| `404` | No fruit exists with the requested `id`                         |
| `422` | Body fails validation (missing, empty or over-long field, negative or non-integer `quantity`, `id` not an integer) |
| `405` | The endpoint exists but does not support the HTTP method used  |

## 6. Errors

Errors use the standard FastAPI body, a `detail` field describing the problem:

```json
{ "detail": "Fruit 99 not found" }
```

Validation errors (`422`) use FastAPI's standard `detail` list, pointing at each
invalid field.

## 7. Persistence

- Storage is a single SQLite file named `fruits.db`, created in the project root on
  application start if it does not exist.
- The `fruits` table is created automatically on start; no migration tool or separate
  database server is required.
- Data survives restarts of the API.
- Each request uses its own short-lived connection; writes are committed when the
  request succeeds and rolled back when it fails.

## 8. Testing

- Unit tests written with `pytest`, run against the API in-process with FastAPI's
  `TestClient` and a temporary SQLite file — no live server and no network.
- Covered: create, read, list, update, delete, `404` for unknown ids on read/update/
  delete, input validation (`422`), whitespace trimming, and that a created fruit is
  actually written to the SQLite file.
- Not covered: performance, concurrency, the exact wire format of the real HTTP
  server, and deployment. See `ADR-001-testing.md`.