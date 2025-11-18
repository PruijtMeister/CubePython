"""
Script to load cube data from local storage or AWS S3.
Downloads cube data dump from S3 if not available locally.
"""

import os
import json
from pathlib import Path
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

# Configuration
LOCAL_DATA_PATH = Path('cube_data/cube_data_dump.json')
LOCAL_FILTERED_DATA_PATH = Path('cube_data/cube_data_dump_filtered.json')
DATA_DIR = Path('cube_data')

# Load environment variables
load_dotenv()


def load_cube_data(filtered=True):
    """
    Load cube data from local file or download from S3 if not present.
    Checks if S3 file is newer and re-downloads if needed.

    Args:
        filtered: If True, return filtered data. If False, return full dataset.

    Returns:
        list: The cube data (filtered or full) loaded from JSON
    """
    # Check if we need to update from S3
    needs_s3_update = False

    if not LOCAL_DATA_PATH.exists():
        print(f"Local file not found: {LOCAL_DATA_PATH}")
        needs_s3_update = True
    elif is_s3_file_newer():
        print("S3 file is newer than local file. Downloading updated version...")
        needs_s3_update = True

    # Download from S3 if needed (this updates both full and filtered dumps)
    if needs_s3_update:
        print("Attempting to download from S3...")
        download_and_process_from_s3()

    # Now load the requested version
    if filtered:
        # Check if filtered file exists
        if not LOCAL_FILTERED_DATA_PATH.exists():
            print("Filtered file not found. Creating from full dump...")
            full_data = load_full_data()
            filtered_data = filter_cubes(full_data)
            save_filtered_data(filtered_data)
            return filtered_data
        else:
            print(f"Loading filtered data from {LOCAL_FILTERED_DATA_PATH}")
            return load_filtered_data()
    else:
        print("Loading full unfiltered data...")
        return load_full_data()


def load_full_data():
    """Load the full unfiltered cube data from local file."""
    print(f"Loading full data from {LOCAL_DATA_PATH}")
    with open(LOCAL_DATA_PATH, 'r') as f:
        data = json.load(f)
    print(f"Successfully loaded {len(data)} cubes (unfiltered)")
    return data


def load_filtered_data():
    """Load the filtered cube data from local file."""
    with open(LOCAL_FILTERED_DATA_PATH, 'r') as f:
        data = json.load(f)
    print(f"Successfully loaded {len(data)} cubes (filtered)")
    return data


def save_filtered_data(filtered_data):
    """Save filtered cube data to local file."""
    print(f"Saving filtered data to {LOCAL_FILTERED_DATA_PATH}")
    with open(LOCAL_FILTERED_DATA_PATH, 'w') as f:
        json.dump(filtered_data, f)
    print(f"Saved {len(filtered_data)} filtered cubes")


def filter_cubes(cube_data):
    """
    Filter cube data to remove unwanted cubes.

    Filters out:
    - Cubes with names starting with 'Clone'
    - Cubes with empty following arrays (less than 1 follower)

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


def get_s3_credentials():
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


def is_s3_file_newer():
    """
    Check if the S3 file is newer than the local file.

    Returns:
        bool: True if S3 file is newer or if there's an error checking
    """
    try:
        # Get credentials
        aws_access_key, aws_secret_key, aws_region, bucket_name, s3_key = get_s3_credentials()

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


def download_and_process_from_s3():
    """
    Download cube data from AWS S3 and create both full and filtered versions.

    This function downloads the full dataset from S3, saves it locally,
    and also creates and saves a filtered version.
    """
    # Get AWS credentials
    aws_access_key, aws_secret_key, aws_region, bucket_name, s3_key = get_s3_credentials()

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
        DATA_DIR.mkdir(exist_ok=True)

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
        filtered_data = filter_cubes(full_data)
        save_filtered_data(filtered_data)

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


def get_cube_by_id(cube_id, cube_data=None):
    """
    Get a specific cube by its shortID.

    Args:
        cube_id: The shortID of the cube to find
        cube_data: Optional pre-loaded cube data. If None, will load data.

    Returns:
        dict: The cube data, or None if not found
    """
    if cube_data is None:
        cube_data = load_cube_data()

    # Assuming cube_data is a list of cubes
    if isinstance(cube_data, list):
        for cube in cube_data:
            if cube.get('shortId') == cube_id or cube.get('shortID') == cube_id:
                return cube
    # Or if it's a dict with cube IDs as keys
    elif isinstance(cube_data, dict):
        return cube_data.get(cube_id)

    return None


def main():
    """Example usage of load_cube_data function."""
    try:
        cube_data = load_cube_data(filtered=True)
        print(f"\n{'='*60}")
        print(f"Total cubes available: {len(cube_data)}")

        # Show a sample cube
        if cube_data and len(cube_data) > 0:
            if isinstance(cube_data, list):
                sample_cube = cube_data[0]
            else:
                sample_cube = list(cube_data.values())[0]

            print(f"\nSample cube:")
            print(f"  ID: {sample_cube.get('shortId') or sample_cube.get('shortID')}")
            print(f"  Name: {sample_cube.get('name')}")
            if 'cards' in sample_cube:
                print(f"  Cards: {len(sample_cube.get('cards', []))}")
            if 'following' in sample_cube:
                print(f"  Followers: {len(sample_cube.get('following', []))}")

    except Exception as e:
        print(f"Error: {e}")
        return 1

    print("\nDone!")
    return 0


if __name__ == '__main__':
    exit(main())
