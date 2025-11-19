"""
Pydantic models for Magic: The Gathering card data.

These models are used for API responses and data validation,
primarily for Scryfall API data.
"""

from pydantic import BaseModel, Field, ConfigDict


class CardModel(BaseModel):
    """
    Pydantic model for MTG card data from Scryfall API.

    This model represents the core card information needed for
    the recommender engine and caching.
    """

    # Core identifiers
    id: str = Field(..., description="Scryfall unique card ID")
    oracle_id: str | None = Field(None, description="Oracle ID for card across all printings")
    name: str = Field(..., description="Card name")

    # Mana and casting
    mana_cost: str | None = Field(None, description="Mana cost (e.g., '{2}{U}{U}')")
    cmc: float = Field(..., description="Converted mana cost")
    type_line: str = Field(..., description="Full type line (e.g., 'Creature — Human Wizard')")

    # Text and rules
    oracle_text: str | None = Field(None, description="Oracle rules text")
    power: str | None = Field(None, description="Power (for creatures)")
    toughness: str | None = Field(None, description="Toughness (for creatures)")
    loyalty: str | None = Field(None, description="Starting loyalty (for planeswalkers)")

    # Colors and identity
    colors: list[str] = Field(default_factory=list, description="Card colors (W, U, B, R, G)")
    color_identity: list[str] = Field(
        default_factory=list, description="Color identity for Commander"
    )

    # Set information
    set: str = Field(..., description="Set code (e.g., 'm21')")
    set_name: str = Field(..., description="Full set name")
    rarity: str = Field(..., description="Card rarity (common, uncommon, rare, mythic)")

    # Legality and metadata
    legalities: dict[str, str] = Field(
        default_factory=dict, description="Format legalities (format: legal/not_legal/banned)"
    )
    keywords: list[str] = Field(default_factory=list, description="Keyword abilities")

    # Images and URIs
    image_uris: dict[str, str] | None = Field(
        None, description="Image URIs for different sizes"
    )
    scryfall_uri: str = Field(..., description="Scryfall web page URL")

    # Prices (optional, may not always be present)
    prices: dict[str, str | None] = Field(
        default_factory=dict, description="Card prices in various currencies"
    )


    model_config = ConfigDict(
        extra='ignore',             # or 'forbid' if you must, but 'ignore' can be slightly cheaper than complex logic
        validate_assignment=False,  # only needed if you assign after creation
        frozen=False,
        arbitrary_types_allowed=False,  # if you don’t need arbitrary types
        revalidate_instances='never',   # if you pass already-valid instances around
        json_schema_extra = {
            "example": {
                "id": "f2b9983e-20d4-4d12-9e2c-ec6d9a345787",
                "oracle_id": "b34bb2dc-c1af-4d77-b0b3-a0fb342a5fc6",
                "name": "Lightning Bolt",
                "mana_cost": "{R}",
                "cmc": 1.0,
                "type_line": "Instant",
                "oracle_text": "Lightning Bolt deals 3 damage to any target.",
                "colors": ["R"],
                "color_identity": ["R"],
                "set": "m21",
                "set_name": "Core Set 2021",
                "rarity": "common",
                "legalities": {"standard": "not_legal", "modern": "legal"},
                "keywords": [],
                "scryfall_uri": "https://scryfall.com/card/m21/123/lightning-bolt",
                "prices": {"usd": "0.25", "eur": "0.20"},
            }
        }
    )
