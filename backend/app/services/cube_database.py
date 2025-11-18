"""
Cube database service for managing CubeCobra cube data.

This module provides a CubeDatabase class that automatically downloads and caches
cube data from CubeCobra when requested by cube ID.
"""

import json
from pathlib import Path
from typing import Any

from app.models.cube import CubeModel


class CubeDatabase:
    """
    Manages CubeCobra cube data with local caching.

    When a cube is requested by ID, this class checks if the cube JSON file exists
    in the local data folder. If not, it fetches the cube data from CubeCobra
    and caches it locally for future use.

    Each cube is stored as a separate JSON file named by its cube ID
    (e.g., `1fdv1.json` for cube ID "1fdv1").

    Attributes:
        data_dir: Path to the directory where cube data is stored
        cubes: Dictionary mapping cube IDs to their data

    Example:
        ```python
        # Instantiate the database
        db = CubeDatabase()

        # Get a cube by ID (will download if needed)
        cube_data = await db.get_cube("1fdv1")

        # Access cube information
        print(cube_data["name"])
        print(cube_data["card_count"])
        ```
    """

    def __init__(self, data_dir: Path | None = None):
        """
        Initialize the CubeDatabase.

        Args:
            data_dir: Optional custom path to the data directory.
                     Defaults to backend/data/cubes.
        """
        if data_dir is None:
            # Default to backend/data/cubes relative to project root
            project_root = Path(__file__).parent.parent.parent.parent
            self.data_dir = project_root / "backend" / "data" / "cubes"
        else:
            self.data_dir = data_dir

        # Create data directory if it doesn't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # In-memory cache of loaded cubes
        self.cubes: dict[str, dict[str, Any]] = {}

    async def get_cube(self, cube_id: str) -> dict[str, Any]:
        """
        Get a cube by its CubeCobra ID.

        If the cube is already in memory, return it immediately.
        If the cube exists locally as a JSON file, load it.
        If the cube doesn't exist locally, fetch it from CubeCobra and cache it.

        Args:
            cube_id: The CubeCobra cube ID (e.g., "1fdv1")

        Returns:
            Dictionary containing the cube data.

        Raises:
            FileNotFoundError: If the cube cannot be found or fetched.
            json.JSONDecodeError: If the cube JSON is invalid.
        """
        # Check in-memory cache first
        if cube_id in self.cubes:
            print(f"Cube {cube_id} found in memory cache")
            return self.cubes[cube_id]

        # Check if cube exists locally
        cube_path = self._get_cube_path(cube_id)
        if cube_path.exists():
            print(f"Cube {cube_id} found locally at {cube_path}")
            cube_data = self._load_cube_from_file(cube_path)
            self.cubes[cube_id] = cube_data
            return cube_data

        # Cube not found locally, fetch it
        print(f"Cube {cube_id} not found locally. Fetching from CubeCobra...")
        cube_data = await self._fetch_and_store_cube(cube_id)
        self.cubes[cube_id] = cube_data
        return cube_data

    def _get_cube_path(self, cube_id: str) -> Path:
        """
        Get the file path for a cube's JSON file.

        Args:
            cube_id: The cube ID

        Returns:
            Path to the cube's JSON file
        """
        return self.data_dir / f"{cube_id}.json"

    def _load_cube_from_file(self, cube_path: Path) -> dict[str, Any]:
        """
        Load a cube from a JSON file.

        Args:
            cube_path: Path to the cube JSON file

        Returns:
            Dictionary containing the cube data

        Raises:
            json.JSONDecodeError: If the file is not valid JSON
        """
        print(f"Loading cube from {cube_path}...")
        with cube_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    async def _fetch_and_store_cube(self, cube_id: str) -> dict[str, Any]:
        """
        Fetch a cube from CubeCobra and store it locally.

        This is a placeholder that will call the actual fetch_cube function
        once it's implemented. For now, it calls the placeholder.

        Args:
            cube_id: The cube ID to fetch

        Returns:
            Dictionary containing the cube data

        Raises:
            NotImplementedError: Until fetch_cube is properly implemented
        """
        # Fetch the cube data
        cube_data = await fetch_cube(cube_id)

        # Store it locally
        cube_path = self._get_cube_path(cube_id)
        self._store_cube(cube_path, cube_data)

        print(f"Successfully fetched and stored cube {cube_id}")
        return cube_data

    def _store_cube(self, cube_path: Path, cube_data: dict[str, Any]) -> None:
        """
        Store cube data to a JSON file.

        Args:
            cube_path: Path where the cube should be stored
            cube_data: The cube data to store
        """
        with cube_path.open("w", encoding="utf-8") as f:
            json.dump(cube_data, f, indent=2, ensure_ascii=False)
        print(f"Stored cube at {cube_path}")

    def get_cached_cube_ids(self) -> list[str]:
        """
        Get a list of all locally cached cube IDs.

        Returns:
            List of cube IDs that have been cached locally
        """
        cube_files = list(self.data_dir.glob("*.json"))
        return [f.stem for f in cube_files]

    def is_cube_cached(self, cube_id: str) -> bool:
        """
        Check if a cube is cached locally.

        Args:
            cube_id: The cube ID to check

        Returns:
            True if the cube exists locally, False otherwise
        """
        return self._get_cube_path(cube_id).exists()


async def fetch_cube(cube_id: str) -> dict[str, Any]:
    """
    Placeholder function to fetch a cube from CubeCobra.

    This function will be implemented later to actually fetch cube data
    from CubeCobra's API or by scraping their website.

    Args:
        cube_id: The CubeCobra cube ID to fetch

    Returns:
        Dictionary containing the cube data

    Raises:
        NotImplementedError: This is a placeholder function
    """
    raise NotImplementedError(
        f"fetch_cube is not yet implemented. "
        f"Cannot fetch cube '{cube_id}' from CubeCobra. "
        f"This function should be implemented to download cube data from CubeCobra."
    )
