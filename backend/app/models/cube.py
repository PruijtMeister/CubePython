"""
Pydantic models for Magic: The Gathering cube data from CubeCobra.

These models are used for API responses and data validation,
primarily for CubeCobra cube data.
"""

from pydantic import BaseModel, Field


class CubeSummaryModel(BaseModel):
    """
    Lightweight Pydantic model for cube summary information.

    This model contains minimal cube information for list views
    and quick lookups without loading full cube data.
    """

    id: str = Field(..., alias="shortId", description="CubeCobra unique cube ID")
    name: str = Field(..., description="Cube name")

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "id": "1fdv1",
                "name": "My Awesome Cube",
            }
        }
    }


class CubeModel(BaseModel):
    """
    Pydantic model for MTG cube data from CubeCobra.

    This model represents the core cube information needed for
    the recommender engine and caching.
    """

    # Core identifiers
    id: str = Field(..., alias="shortId", description="CubeCobra unique cube ID")
    name: str = Field(..., description="Cube name")

    # Cube metadata
    owner: str | None = Field(None, description="Cube owner username")
    description: str | None = Field(None, description="Cube description")
    card_count: int = Field(0, alias="cardCount", description="Number of cards in the cube")

    # Categories and tags
    category_override: str | None = Field(None, alias="categoryOverride", description="Custom category")
    category_prefixes: list[str] = Field(
        default_factory=list, alias="categoryPrefixes", description="Category prefixes"
    )
    tags: list[str] = Field(default_factory=list, description="Cube tags")

    # Card list (simplified for now - can be expanded later)
    card_ids: list[int] = Field(
        alias="cards", default_factory=list, description="List of cards in the cube"
    )

    # Metadata
    is_listed: bool = Field(True, alias="isListed", description="Whether cube is publicly listed")
    is_private: bool = Field(False, alias="isPrivate", description="Whether cube is private")
    date_updated: str | None = Field(None, alias="dateUpdated", description="Last update timestamp")

    model_config = {
        "populate_by_name": True,
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
