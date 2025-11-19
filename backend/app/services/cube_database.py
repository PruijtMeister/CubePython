"""
Cube database service for managing CubeCobra cube data.

This module provides a CubeDatabase class that loads cube data from local storage
or downloads from S3 if needed, and provides fast lookups by cube ID.
"""

import os
import json
from pathlib import Path
from typing import Any
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv
from pydantic import TypeAdapter

from app.models.cube import CubeModel

# Load environment variables
load_dotenv()

# Configuration
LOCAL_DATA_PATH = Path('data/cube/cube_data_dump.json')
LOCAL_FILTERED_DATA_PATH = Path('data/cube/cube_data_dump_filtered.json')
DATA_DIR = Path('data/cube')


class CubeDatabase:
    """
    Manages CubeCobra cube data loaded from local storage or S3.

    This class loads the complete cube database from local storage,
    downloading from S3 if the local file doesn't exist or is outdated.

    The data is automatically synced with S3 on initialization, downloading
    updates if the S3 file is newer than the local cache.

    Attributes:
        cube_data: The full cube dataset loaded from local storage/S3
        cube_index: Dictionary mapping cube IDs to their data for fast lookup
        use_filtered: Whether to use filtered data (default: True)

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

    def __init__(self, use_filtered: bool = True):
        """
        Initialize the CubeDatabase.

        Loads the cube data from local cache or S3, checking for updates.

        Args:
            use_filtered: If True, use filtered data (removes clones and low-follower cubes)
        """
        self.use_filtered = use_filtered
        print("Loading cube data from local storage/S3...")
        self.cube_data: list[CubeModel] = self._load_cube_data()

        # Build index for fast lookups
        print("Building cube index...")
        self.cube_index: dict[str, CubeModel] = {}

        for cube in self.cube_data:
            cube_id = cube.id
            if cube_id:
                self.cube_index[cube_id] = cube

        print(f"CubeDatabase ready with {len(self.cube_index)} cubes")

    def _load_cube_data(self) -> list[CubeModel]:
        """
        Load cube data from local file or download from S3 if not present.
        Checks if S3 file is newer and re-downloads if needed.

        Returns:
            list: The cube data (filtered or full) loaded from JSON
        """
        # Check if we need to update from S3
        needs_s3_update = False

        if not LOCAL_DATA_PATH.exists():
            print(f"Local file not found: {LOCAL_DATA_PATH}")
            needs_s3_update = True
        elif self._is_s3_file_newer():
            print("S3 file is newer than local file. Downloading updated version...")
            needs_s3_update = True

        # Download from S3 if needed (this updates both full and filtered dumps)
        if needs_s3_update:
            print("Attempting to download from S3...")
            self._download_and_process_from_s3()

        print("Loading full unfiltered data...")
        cube_data = self._load_full_data()

        adapter = TypeAdapter(list[CubeModel])
        return adapter.validate_python(cube_data)
        return adapter.model_construct(cube_data)

        return [CubeModel.model_construct(row) for row in cube_data]
        # return [CubeModel.model_validate(row) for row in cube_data[:100]]

    def _load_full_data(self) -> list[dict[str, Any]]:
        """Load the full unfiltered cube data from local file."""
        print(f"Loading full data from {LOCAL_DATA_PATH}")
        with open(LOCAL_DATA_PATH, 'r') as f:
            data = json.load(f)
        print(f"Successfully loaded {len(data)} cubes (unfiltered)")
        return data

    def _load_filtered_data(self) -> list[dict[str, Any]]:
        """Load the filtered cube data from local file."""
        with open(LOCAL_FILTERED_DATA_PATH, 'r') as f:
            data = json.load(f)
        print(f"Successfully loaded {len(data)} cubes (filtered)")
        return data

    def _save_filtered_data(self, filtered_data: list[dict[str, Any]]) -> None:
        """Save filtered cube data to local file."""
        print(f"Saving filtered data to {LOCAL_FILTERED_DATA_PATH}")
        with open(LOCAL_FILTERED_DATA_PATH, 'w') as f:
            json.dump(filtered_data, f)
        print(f"Saved {len(filtered_data)} filtered cubes")

    def _filter_cubes(self, cube_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Filter cube data to remove unwanted cubes.

        Filters out:
        - Cubes with names starting with 'Clone'
        - Cubes with empty following arrays (less than 2 followers)

        Args:
            cube_data: List of cube dictionaries

        Returns:
            list: Filtered cube data
        """
        if not isinstance(cube_data, list):
            return cube_data

        original_count = len(cube_data)

        filtered_data = [
            cube for cube in cube_data
            if not cube.get('name', '').startswith('Clone')
            and len(cube.get('following', [])) >= 2
        ]

        filtered_count = original_count - len(filtered_data)
        print(f"Filtered out {filtered_count} cubes ({len(filtered_data)} remaining)")

        return filtered_data

    def _get_s3_credentials(self) -> tuple[str, str, str, str, str]:
        """
        Get AWS credentials from environment variables.

        Returns:
            tuple: (access_key, secret_key, region, bucket_name, s3_key)
        """
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_region = os.getenv('AWS_REGION', 'us-east-1')
        bucket_name = os.getenv('S3_BUCKET_NAME')
        s3_key = os.getenv('S3_CUBE_DATA_KEY')

        if not all([aws_access_key, aws_secret_key, bucket_name, s3_key]):
            raise ValueError(
                "Missing AWS credentials. Please set the following environment variables:\n"
                "  AWS_ACCESS_KEY_ID\n"
                "  AWS_SECRET_ACCESS_KEY\n"
                "  S3_BUCKET_NAME\n"
                "  S3_CUBE_DATA_KEY\n"
                "You can copy .env.example to .env and fill in your credentials."
            )

        return aws_access_key, aws_secret_key, aws_region, bucket_name, s3_key

    def _is_s3_file_newer(self) -> bool:
        """
        Check if the S3 file is newer than the local file.

        Returns:
            bool: True if S3 file is newer or if there's an error checking
        """
        try:
            # Get credentials
            aws_access_key, aws_secret_key, aws_region, bucket_name, s3_key = self._get_s3_credentials()

            # Create S3 client
            s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region
            )

            # Get S3 object metadata
            response = s3_client.head_object(Bucket=bucket_name, Key=s3_key)
            s3_last_modified = response['LastModified']

            # Get local file modification time
            local_mtime = os.path.getmtime(LOCAL_DATA_PATH)
            local_last_modified = local_mtime

            # Convert to comparable format (timestamps)
            s3_timestamp = s3_last_modified.timestamp()

            print(f"Local file last modified: {os.path.getctime(LOCAL_DATA_PATH)}")
            print(f"S3 file last modified: {s3_last_modified}")

            # Return True if S3 is newer
            return s3_timestamp > local_last_modified

        except (NoCredentialsError, ClientError, ValueError) as e:
            print(f"Warning: Could not check S3 file age: {e}")
            print("Assuming local file is current...")
            return False
        except Exception as e:
            print(f"Warning: Unexpected error checking S3 file age: {e}")
            print("Assuming local file is current...")
            return False

    def _download_and_process_from_s3(self) -> None:
        """
        Download cube data from AWS S3 and create both full and filtered versions.

        This function downloads the full dataset from S3, saves it locally,
        and also creates and saves a filtered version.
        """
        # Get AWS credentials
        aws_access_key, aws_secret_key, aws_region, bucket_name, s3_key = self._get_s3_credentials()

        print(f"Downloading from S3: s3://{bucket_name}/{s3_key}")

        try:
            # Create S3 client
            s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region
            )

            # Create data directory if it doesn't exist
            DATA_DIR.mkdir(parents=True, exist_ok=True)

            # Download file
            print("Downloading... (this may take a while for a 330MB file)")
            s3_client.download_file(bucket_name, s3_key, str(LOCAL_DATA_PATH))
            print(f"Successfully downloaded to: {LOCAL_DATA_PATH}")

            # Load the data
            with open(LOCAL_DATA_PATH, 'r') as f:
                full_data = json.load(f)

            print(f"Successfully loaded {len(full_data)} cubes from S3")

            # Create and save filtered version
            print("Creating filtered version...")
            filtered_data = self._filter_cubes(full_data)
            self._save_filtered_data(filtered_data)

        except NoCredentialsError:
            raise ValueError("AWS credentials not found or invalid")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                raise ValueError(f"File not found in S3: s3://{bucket_name}/{s3_key}")
            else:
                raise ValueError(f"AWS Error: {e}")
        except Exception as e:
            raise ValueError(f"Error downloading from S3: {e}")

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

    def get_all_cube_summaries(self) -> list[dict[str, str]]:
        """
        Get a list of all cubes with their ID and name.

        Returns:
            List of dictionaries containing cube shortId and name
        """
        summaries = []
        for cube_id, cube_data in self.cube_index.items():
            summaries.append({
                "shortId": cube_id,
                "name": cube_data.name
            })
        return summaries

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
