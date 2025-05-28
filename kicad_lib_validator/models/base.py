from pydantic import BaseModel


class Position(BaseModel):
    """Represents a 2D position with x and y coordinates."""

    x: float
    y: float


class Size(BaseModel):
    """Represents a 2D size with width and height."""

    width: float
    height: float
