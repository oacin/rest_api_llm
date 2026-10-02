"""Tests for the fruit endpoints."""

import sqlite3


def test_list_fruits_is_empty_for_a_new_inventory(client):
    response = client.get("/fruits")

    assert response.status_code == 200
    assert response.json() == []


def test_create_fruit_returns_201_with_an_assigned_id(client):
    response = client.post(
        "/fruits", json={"name": "Apple", "color": "red", "quantity": 12}
    )

    assert response.status_code == 201
    assert response.json() == {"id": 1, "name": "Apple", "color": "red", "quantity": 12}


def test_create_fruit_trims_surrounding_whitespace(client):
    response = client.post(
        "/fruits", json={"name": "  Apple  ", "color": "\tred ", "quantity": 0}
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Apple"
    assert response.json()["color"] == "red"


def test_created_fruit_is_persisted_in_the_sqlite_file(client, db_path, create_fruit):
    fruit = create_fruit()

    connection = sqlite3.connect(db_path)
    try:
        row = connection.execute(
            "SELECT name, color, quantity FROM fruits WHERE id = ?", (fruit["id"],)
        ).fetchone()
    finally:
        connection.close()

    assert row == ("Apple", "red", 12)


def test_get_fruit_returns_the_fruit(client, create_fruit):
    fruit = create_fruit()

    response = client.get(f"/fruits/{fruit['id']}")

    assert response.status_code == 200
    assert response.json() == fruit


def test_get_unknown_fruit_returns_404(client):
    response = client.get("/fruits/99")

    assert response.status_code == 404
    assert response.json()["detail"] == "Fruit 99 not found"


def test_get_fruit_with_non_integer_id_returns_422(client):
    response = client.get("/fruits/apple")

    assert response.status_code == 422


def test_list_fruits_returns_all_fruits_ordered_by_id(client, create_fruit):
    first = create_fruit()
    second = create_fruit(name="Banana", color="yellow", quantity=0)

    response = client.get("/fruits")

    assert response.status_code == 200
    assert response.json() == [first, second]


def test_update_fruit_replaces_all_fields(client, create_fruit):
    fruit = create_fruit()

    response = client.put(
        f"/fruits/{fruit['id']}",
        json={"name": "Green Apple", "color": "green", "quantity": 5},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": fruit["id"],
        "name": "Green Apple",
        "color": "green",
        "quantity": 5,
    }
    assert client.get(f"/fruits/{fruit['id']}").json() == response.json()


def test_update_unknown_fruit_returns_404(client):
    response = client.put(
        "/fruits/99", json={"name": "Apple", "color": "red", "quantity": 1}
    )

    assert response.status_code == 404
    assert client.get("/fruits").json() == []


def test_delete_fruit_returns_204_and_removes_it(client, create_fruit):
    fruit = create_fruit()

    response = client.delete(f"/fruits/{fruit['id']}")

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/fruits/{fruit['id']}").status_code == 404
    assert client.get("/fruits").json() == []


def test_delete_unknown_fruit_returns_404(client):
    response = client.delete("/fruits/99")

    assert response.status_code == 404


def test_delete_twice_returns_404_the_second_time(client, create_fruit):
    fruit = create_fruit()
    assert client.delete(f"/fruits/{fruit['id']}").status_code == 204

    response = client.delete(f"/fruits/{fruit['id']}")

    assert response.status_code == 404


def test_create_fruit_without_name_returns_422(client):
    response = client.post("/fruits", json={"color": "red", "quantity": 1})

    assert response.status_code == 422


def test_create_fruit_with_blank_name_returns_422(client):
    response = client.post(
        "/fruits", json={"name": "   ", "color": "red", "quantity": 1}
    )

    assert response.status_code == 422


def test_create_fruit_with_negative_quantity_returns_422(client):
    response = client.post(
        "/fruits", json={"name": "Apple", "color": "red", "quantity": -1}
    )

    assert response.status_code == 422


def test_create_fruit_with_non_integer_quantity_returns_422(client):
    response = client.post(
        "/fruits", json={"name": "Apple", "color": "red", "quantity": "many"}
    )

    assert response.status_code == 422


def test_create_fruit_with_too_long_name_returns_422(client):
    response = client.post(
        "/fruits", json={"name": "A" * 101, "color": "red", "quantity": 1}
    )

    assert response.status_code == 422


def test_update_fruit_with_negative_quantity_returns_422(client, create_fruit):
    fruit = create_fruit()

    response = client.put(
        f"/fruits/{fruit['id']}",
        json={"name": "Apple", "color": "red", "quantity": -3},
    )

    assert response.status_code == 422
    assert client.get(f"/fruits/{fruit['id']}").json() == fruit