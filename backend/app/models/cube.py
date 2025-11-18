"""
Pydantic models for Magic: The Gathering cube data from CubeCobra.

These models are used for API responses and data validation,
primarily for CubeCobra cube data.
"""

from pydantic import BaseModel, Field


class CubeModel(BaseModel):
    """
    Pydantic model for MTG cube data from CubeCobra.

    This model represents the core cube information needed for
    the recommender engine and caching.
    """

    # Core identifiers
    id: str = Field(..., description="CubeCobra unique cube ID")
    name: str = Field(..., description="Cube name")

    # Cube metadata
    owner: str | None = Field(None, description="Cube owner username")
    description: str | None = Field(None, description="Cube description")
    card_count: int = Field(0, description="Number of cards in the cube")

    # Categories and tags
    category_override: str | None = Field(None, description="Custom category")
    category_prefixes: list[str] = Field(
        default_factory=list, description="Category prefixes"
    )
    tags: list[str] = Field(default_factory=list, description="Cube tags")

    # Card list (simplified for now - can be expanded later)
    cards: list[dict] = Field(
        default_factory=list, description="List of cards in the cube"
    )

    # Metadata
    is_listed: bool = Field(True, description="Whether cube is publicly listed")
    is_private: bool = Field(False, description="Whether cube is private")
    date_updated: str | None = Field(None, description="Last update timestamp")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "1fdv1",
                "name": "My Awesome Cube",
                "owner": "cubebuilder123",
                "description": "A balanced 360 card cube focusing on synergy",
                "card_count": 360,
                "category_override": "Vintage",
                "category_prefixes": ["Vintage"],
                "tags": ["powered", "balanced"],
                "cards": [],
                "is_listed": True,
                "is_private": False,
                "date_updated": "2024-01-15T12:00:00Z",
            }
        }
    }
