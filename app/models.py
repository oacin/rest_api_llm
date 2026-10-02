"""Pydantic models describing the fruit payloads."""

from pydantic import BaseModel, ConfigDict, Field


class Fruit(BaseModel):
    """A fruit as returned by the API."""

    id: int
    name: str
    color: str
    quantity: int


class FruitCreate(BaseModel):
    """Body accepted by POST /fruits."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100, examples=["Apple"])
    color: str = Field(min_length=1, max_length=50, examples=["red"])
    quantity: int = Field(ge=0, examples=[12])


class FruitUpdate(BaseModel):
    """Body accepted by PUT /fruits/{id}; replaces all writable fields."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100, examples=["Green Apple"])
    color: str = Field(min_length=1, max_length=50, examples=["green"])
    quantity: int = Field(ge=0, examples=[8])