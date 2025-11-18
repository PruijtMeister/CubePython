# Import all models here so they are registered with SQLModel
# Example:
# from app.models.card import Card
from app.models.card import CardModel
from app.models.cube import CubeModel

__all__ = ["CardModel", "CubeModel"]
