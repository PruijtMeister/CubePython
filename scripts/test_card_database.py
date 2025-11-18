"""
Test script for CardDatabase service.

This script demonstrates the CardDatabase functionality by:
1. Initializing the database (downloading if needed)
2. Performing sample queries
3. Displaying card information

Run from project root:
    python scripts/test_card_database.py
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path so we can import the service
project_root = Path(__file__).parent.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from app.services.card_database import CardDatabase


async def main():
    """Run CardDatabase tests."""
    print("=" * 80)
    print("CardDatabase Test Script")
    print("=" * 80)
    print()

    # Initialize the database
    print("Initializing CardDatabase...")
    db = await CardDatabase.create()
    print()

    # Show database stats
    print(f"Total cards loaded: {len(db.cards)}")
    print()

    # Test 1: Search by exact name
    print("-" * 80)
    print("Test 1: Search for 'Lightning Bolt' by exact name")
    print("-" * 80)
    card = db.get_card_by_name("Lightning Bolt")
    if card:
        print(f"Found: {card.get('name')}")
        print(f"  Type: {card.get('type_line')}")
        print(f"  Mana Cost: {card.get('mana_cost', 'N/A')}")
        print(f"  Oracle Text: {card.get('oracle_text', 'N/A')}")
        print(f"  Set: {card.get('set_name', 'N/A')} ({card.get('set', 'N/A')})")
    else:
        print("Not found")
    print()

    # Test 2: Text search
    print("-" * 80)
    print("Test 2: Search for cards containing 'bolt' (limit 5)")
    print("-" * 80)
    results = db.search_cards("bolt", limit=5)
    for i, card in enumerate(results, 1):
        print(f"{i}. {card.get('name')} - {card.get('type_line')}")
    print()

    # Test 3: Search by Oracle ID
    print("-" * 80)
    print("Test 3: Find all printings of 'Sol Ring'")
    print("-" * 80)
    sol_ring = db.get_card_by_name("Sol Ring")
    if sol_ring:
        oracle_id = sol_ring.get("oracle_id")
        printings = db.get_cards_by_oracle_id(oracle_id)
        print(f"Found {len(printings)} printings of Sol Ring:")
        for i, card in enumerate(printings[:5], 1):  # Show first 5
            print(f"{i}. {card.get('set_name')} ({card.get('set')}) - {card.get('rarity')}")
        if len(printings) > 5:
            print(f"... and {len(printings) - 5} more")
    else:
        print("Sol Ring not found")
    print()

    # Test 4: Show some interesting stats
    print("-" * 80)
    print("Test 4: Database Statistics")
    print("-" * 80)

    # Count unique oracle IDs
    oracle_ids = set()
    for card in db.cards:
        if card.get("oracle_id"):
            oracle_ids.add(card.get("oracle_id"))

    print(f"Total cards: {len(db.cards)}")
    print(f"Unique Oracle IDs: {len(oracle_ids)}")
    print()

    print("=" * 80)
    print("All tests completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
