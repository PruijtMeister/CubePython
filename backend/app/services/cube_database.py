"""
Cube database service for managing CubeCobra cube data.

This module provides a CubeDatabase class that loads cube data from the S3 dump
and provides fast lookups by cube ID.
"""

import sys
from pathlib import Path
from typing import Any

# Add scripts directory to path to import load_cube_data
scripts_dir = Path(__file__).parent.parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from scripts.load_cube_data import load_cube_data


class CubeDatabase:
    """
    Manages CubeCobra cube data loaded from S3 dump.

    This class loads the complete cube database from the S3 data dump
    (managed by load_cube_data.py) and provides fast in-memory lookups.

    The data is automatically synced with S3 on initialization, downloading
    updates if the S3 file is newer than the local cache.

    Attributes:
        cube_data: The full cube dataset loaded from S3
        cube_index: Dictionary mapping cube IDs to their data for fast lookup

    Example:
        ```python
        # Instantiate the database (loads from S3 if needed)
        db = CubeDatabase()

        # Get a cube by ID
        cube_data = db.get_cube("1fdv1")

        # Access cube information
        print(cube_data["name"])
        print(cube_data.get("card_count"))
        ```
    """

    def __init__(self):
        """
        Initialize the CubeDatabase.

        Loads the cube data from local cache or S3, checking for updates.
        """
        print("Loading cube data from S3/cache...")
        self.cube_data = load_cube_data()

        # Build index for fast lookups
        print("Building cube index...")
        self.cube_index: dict[str, dict[str, Any]] = {}

        if isinstance(self.cube_data, list):
            for cube in self.cube_data:
                cube_id = cube.get('shortId') or cube.get('shortID')
                if cube_id:
                    self.cube_index[cube_id] = cube
        elif isinstance(self.cube_data, dict):
            self.cube_index = self.cube_data

        print(f"CubeDatabase ready with {len(self.cube_index)} cubes")

    def get_cube(self, cube_id: str) -> dict[str, Any] | None:
        """
        Get a cube by its CubeCobra ID.

        Args:
            cube_id: The CubeCobra cube ID (e.g., "1fdv1")

        Returns:
            Dictionary containing the cube data, or None if not found.
        """
        return self.cube_index.get(cube_id)

    def get_all_cube_ids(self) -> list[str]:
        """
        Get a list of all cube IDs in the database.

        Returns:
            List of all cube IDs
        """
        return list(self.cube_index.keys())

    def search_cubes(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """
        Search for cubes by name.

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            List of cubes matching the query
        """
        query_lower = query.lower()
        results = []

        for cube in self.cube_index.values():
            name = cube.get('name', '')
            if query_lower in name.lower():
                results.append(cube)
                if len(results) >= limit:
                    break

        return results

    def get_cube_count(self) -> int:
        """
        Get the total number of cubes in the database.

        Returns:
            Number of cubes
        """
        return len(self.cube_index)
