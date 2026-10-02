"""FastAPI application exposing the Fruit Inventory endpoints."""

import sqlite3
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Response

from app.database import get_db, init_db
from app.models import Fruit, FruitCreate, FruitUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create the database file and tables before serving requests."""
    init_db()
    yield


app = FastAPI(
    title="Fruit Inventory API",
    description="A small CRUD API that keeps track of fruits in an inventory.",
    version="0.1.0",
    lifespan=lifespan,
)


def fetch_fruit_or_404(db: sqlite3.Connection, fruit_id: int) -> dict:
    """Return the fruit with the given id, or raise a 404 error."""
    row = db.execute(
        "SELECT id, name, color, quantity FROM fruits WHERE id = ?", (fruit_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Fruit {fruit_id} not found")
    return dict(row)


@app.get("/fruits", response_model=list[Fruit])
def list_fruits(db: sqlite3.Connection = Depends(get_db)):
    """List all fruits, ordered by id."""
    rows = db.execute(
        "SELECT id, name, color, quantity FROM fruits ORDER BY id"
    ).fetchall()
    return [dict(row) for row in rows]


@app.get("/fruits/{fruit_id}", response_model=Fruit)
def get_fruit(fruit_id: int, db: sqlite3.Connection = Depends(get_db)):
    """Return a single fruit by id."""
    return fetch_fruit_or_404(db, fruit_id)


@app.post("/fruits", response_model=Fruit, status_code=201)
def create_fruit(fruit: FruitCreate, db: sqlite3.Connection = Depends(get_db)):
    """Create a fruit and return it, including the assigned id."""
    cursor = db.execute(
        "INSERT INTO fruits (name, color, quantity) VALUES (?, ?, ?)",
        (fruit.name, fruit.color, fruit.quantity),
    )
    return {"id": cursor.lastrowid, **fruit.model_dump()}


@app.put("/fruits/{fruit_id}", response_model=Fruit)
def update_fruit(
    fruit_id: int, fruit: FruitUpdate, db: sqlite3.Connection = Depends(get_db)
):
    """Replace all writable fields of a fruit."""
    fetch_fruit_or_404(db, fruit_id)
    db.execute(
        "UPDATE fruits SET name = ?, color = ?, quantity = ? WHERE id = ?",
        (fruit.name, fruit.color, fruit.quantity, fruit_id),
    )
    return {"id": fruit_id, **fruit.model_dump()}


@app.delete("/fruits/{fruit_id}", status_code=204, response_class=Response)
def delete_fruit(fruit_id: int, db: sqlite3.Connection = Depends(get_db)):
    """Delete a fruit. Returns 204 with an empty body."""
    fetch_fruit_or_404(db, fruit_id)
    db.execute("DELETE FROM fruits WHERE id = ?", (fruit_id,))
    return Response(status_code=204)