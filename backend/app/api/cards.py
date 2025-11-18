"""
API routes for card-related endpoints.
"""

from fastapi import APIRouter, HTTPException, Request

from app.models.card import CardModel

router = APIRouter()


@router.get("/{card_id}")
async def get_card_by_id(card_id: str, request: Request) -> CardModel:
    """
    Get a card by its Scryfall ID.

    Args:
        card_id: The Scryfall card ID to look up

    Returns:
        Card data model

    Raises:
        HTTPException: 404 if card not found
    """
    # Access the CardDatabase from app state
    card_db = request.app.state.card_db

    # Search for the card by ID
    for card in card_db.cards:
        if card.get("id") == card_id:
            return CardModel.model_validate(card)

    raise HTTPException(
        status_code=404,
        detail=f"Card with ID '{card_id}' not found"
    )


@router.get("/name/{card_name}")
async def get_card_by_name(card_name: str, request: Request) -> CardModel:
    """
    Get a card by its exact name.

    Args:
        card_name: The exact card name to look up

    Returns:
        Card data model

    Raises:
        HTTPException: 404 if card not found
    """
    card_db = request.app.state.card_db
    card = card_db.get_card_by_name(card_name)

    if not card:
        raise HTTPException(
            status_code=404,
            detail=f"Card with name '{card_name}' not found"
        )

    return CardModel.model_validate(card)


@router.get("/search/{query}")
async def search_cards(
    query: str,
    request: Request,
    limit: int = 10
) -> list[CardModel]:
    """
    Search for cards by name (case-insensitive partial match).

    Args:
        query: Search string to match against card names
        limit: Maximum number of results to return (default: 10)

    Returns:
        List of matching card data models
    """
    card_db = request.app.state.card_db
    results = card_db.search_cards(query, limit=limit)

    return [CardModel.model_validate(card) for card in results]
