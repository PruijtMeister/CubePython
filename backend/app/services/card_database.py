"""
Card database service for managing Scryfall Oracle Cards bulk data.

This module provides a CardDatabase class that automatically downloads and caches
the Scryfall Oracle Cards dataset when instantiated.
"""

import json
from pathlib import Path
from typing import Any

import httpx

from app.core.config import settings


class CardDatabase:
    """
    Manages the Scryfall Oracle Cards bulk data.

    When instantiated, this class checks if the Oracle Cards JSON file exists
    in the data folder. If not, it fetches the latest version from Scryfall's
    Bulk Data API and downloads it.

    The Oracle Cards dataset contains one card object for each Oracle ID on Scryfall,
    providing comprehensive card information including rules text, types, mana costs,
    and legalities.

    Attributes:
        data_dir: Path to the directory where card data is stored
        oracle_cards_path: Path to the oracle-cards.json file
        cards: List of card dictionaries loaded from the Oracle Cards file

    Example:
        ```python
        # Instantiate the database (will download if needed)
        db = await CardDatabase.create()

        # Access the cards
        for card in db.cards:
            print(card['name'])
        ```
    """

    BULK_DATA_ENDPOINT = f"{settings.scryfall_api_url}/bulk-data"
    ORACLE_CARDS_TYPE = "oracle_cards"
    ORACLE_CARDS_FILENAME = "oracle-cards.json"

    def __init__(self, data_dir: Path | None = None):
        """
        Initialize the CardDatabase.

        Note: Use the `create()` class method instead of this constructor
        to ensure the database is properly initialized with data downloaded.

        Args:
            data_dir: Optional custom path to the data directory.
                     Defaults to backend/data/cards.
        """
        if data_dir is None:
            # Default to backend/data/cards relative to project root
            project_root = Path(__file__).parent.parent.parent.parent
            self.data_dir = project_root / "backend" / "data" / "cards"
        else:
            self.data_dir = data_dir

        self.oracle_cards_path = self.data_dir / self.ORACLE_CARDS_FILENAME
        self.cards: list[dict[str, Any]] = []

    @classmethod
    async def create(cls, data_dir: Path | None = None) -> "CardDatabase":
        """
        Create and initialize a CardDatabase instance.

        This factory method creates a CardDatabase instance and ensures
        the Oracle Cards data is available, downloading it if necessary.

        Args:
            data_dir: Optional custom path to the data directory.

        Returns:
            Initialized CardDatabase instance with cards loaded.

        Raises:
            httpx.HTTPError: If download from Scryfall fails.
            json.JSONDecodeError: If the downloaded file is not valid JSON.
        """
        instance = cls(data_dir)
        await instance._ensure_data()
        instance._load_cards()
        return instance

    async def _ensure_data(self) -> None:
        """
        Ensure the Oracle Cards data exists, downloading if necessary.

        Checks if the oracle-cards.json file exists. If not, fetches the
        bulk data list from Scryfall and downloads the Oracle Cards dataset.
        """
        if self.oracle_cards_path.exists():
            print(f"Oracle Cards data found at {self.oracle_cards_path}")
            return

        print("Oracle Cards data not found. Downloading from Scryfall...")
        await self._download_oracle_cards()

    async def _download_oracle_cards(self) -> None:
        """
        Download the Oracle Cards dataset from Scryfall.

        Steps:
        1. Fetch the list of available bulk data files from Scryfall
        2. Find the Oracle Cards bulk data object
        3. Download the file from the download_uri
        4. Save to the data directory

        Raises:
            httpx.HTTPError: If any HTTP request fails.
            ValueError: If Oracle Cards bulk data is not found.
        """
        async with httpx.AsyncClient() as client:
            # Step 1: Get the list of bulk data objects
            print(f"Fetching bulk data list from {self.BULK_DATA_ENDPOINT}...")
            response = await client.get(self.BULK_DATA_ENDPOINT)
            response.raise_for_status()

            bulk_data = response.json()

            # Step 2: Find the Oracle Cards object
            oracle_cards_obj = None
            for item in bulk_data.get("data", []):
                if item.get("type") == self.ORACLE_CARDS_TYPE:
                    oracle_cards_obj = item
                    break

            if not oracle_cards_obj:
                raise ValueError(
                    f"Oracle Cards bulk data not found. "
                    f"Available types: {[item.get('type') for item in bulk_data.get('data', [])]}"
                )

            download_uri = oracle_cards_obj.get("download_uri")
            if not download_uri:
                raise ValueError("Oracle Cards object missing download_uri")

            # Print info about the download
            size_mb = oracle_cards_obj.get("size", 0) / (1024 * 1024)
            print(f"Found Oracle Cards dataset:")
            print(f"  Name: {oracle_cards_obj.get('name')}")
            print(f"  Description: {oracle_cards_obj.get('description')}")
            print(f"  Size: {size_mb:.2f} MB")
            print(f"  Updated: {oracle_cards_obj.get('updated_at')}")
            print(f"Downloading from {download_uri}...")

            # Step 3: Download the file
            # Use streaming to handle large files efficiently
            self.data_dir.mkdir(parents=True, exist_ok=True)

            async with client.stream("GET", download_uri) as response:
                response.raise_for_status()

                with self.oracle_cards_path.open("wb") as f:
                    total_downloaded = 0
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        f.write(chunk)
                        total_downloaded += len(chunk)
                        # Print progress every 10 MB
                        if total_downloaded % (10 * 1024 * 1024) < 8192:
                            downloaded_mb = total_downloaded / (1024 * 1024)
                            print(f"  Downloaded {downloaded_mb:.2f} MB...")

            print(f"Successfully downloaded Oracle Cards to {self.oracle_cards_path}")

    def _load_cards(self) -> None:
        """
        Load cards from the oracle-cards.json file into memory.

        Raises:
            json.JSONDecodeError: If the file is not valid JSON.
            FileNotFoundError: If the oracle-cards.json file doesn't exist.
        """
        print(f"Loading cards from {self.oracle_cards_path}...")
        with self.oracle_cards_path.open("r", encoding="utf-8") as f:
            self.cards = json.load(f)
        print(f"Loaded {len(self.cards)} cards")

    def get_card_by_name(self, name: str) -> dict[str, Any] | None:
        """
        Get a card by its exact name.

        Args:
            name: The exact card name to search for.

        Returns:
            Card dictionary if found, None otherwise.
        """
        for card in self.cards:
            if card.get("name") == name:
                return card
        return None

    def get_cards_by_oracle_id(self, oracle_id: str) -> list[dict[str, Any]]:
        """
        Get all printings of a card by Oracle ID.

        Args:
            oracle_id: The Oracle ID to search for.

        Returns:
            List of card dictionaries with the matching Oracle ID.
        """
        return [card for card in self.cards if card.get("oracle_id") == oracle_id]

    def search_cards(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """
        Simple card name search.

        Args:
            query: Search string to match against card names (case-insensitive).
            limit: Maximum number of results to return.

        Returns:
            List of matching card dictionaries.
        """
        query_lower = query.lower()
        results = []

        for card in self.cards:
            if query_lower in card.get("name", "").lower():
                results.append(card)
                if len(results) >= limit:
                    break

        return results
