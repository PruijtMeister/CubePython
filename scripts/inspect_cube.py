"""
Simple script to inspect and dump the contents of CubeCobra cube pages.
Extracts window.ReactProps from the page which contains all the cube data.
Can process a single cube or a list of cube shortIDs from a JSON file.
"""

import json
import re
import time
import requests
from bs4 import BeautifulSoup
from pathlib import Path

# Configuration
INPUT_SHORT_IDS_FILE = 'output_cube_short_ids.json'  # File with list of shortIDs
OUTPUT_DIR = 'cube_data'  # Directory to save cube data
RATE_LIMIT_DELAY = 0.5  # Delay between requests in seconds (2 requests per second)


def extract_react_props(html_content):
    """Extract window.ReactProps from the HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all script tags in the body
    body = soup.find('body')
    if not body:
        return None

    scripts = body.find_all('script')

    for script in scripts:
        if script.string and 'window.reactProps' in script.string:
            # Extract the JSON object assigned to window.ReactProps
            # Pattern: window.ReactProps = {...};
            match = re.search(r'window\.reactProps\s*=\s*(\{.*?\});', script.string, re.DOTALL)
            if match:
                json_str = match.group(1)
                # Replace JavaScript undefined with JSON null
                json_str = re.sub(r'\bundefined\b', 'null', json_str)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    print(f"Error parsing ReactProps JSON: {e}")
                    print(f"First 500 chars of JSON: {json_str[:500]}")
                    return None

    return None


def fetch_cube_data(cube_id, headers, output_dir):
    """Fetch and save data for a single cube."""
    url = f'https://cubecobra.com/cube/overview/{cube_id}'
    print(f"  Fetching: {url}")

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Extract ReactProps
        react_props = extract_react_props(response.text)

        if react_props:
            # Save ReactProps as JSON
            output_file = output_dir / f'{cube_id}.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(react_props, f, indent=2)

            # Print cube info
            if 'cube' in react_props:
                cube = react_props['cube']
                name = cube.get('name', 'Unknown')
                card_count = cube.get('card_count', 0)
                print(f"    ✓ {name} ({card_count} cards)")
            else:
                print(f"    ✓ Saved")

            return True
        else:
            print(f"    ✗ Could not find window.reactProps")
            return False

    except requests.exceptions.RequestException as e:
        print(f"    ✗ Error: {e}")
        return False


def main():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    # Create output directory
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True)

    # Check if input file exists
    input_file = Path(INPUT_SHORT_IDS_FILE)
    if input_file.exists():
        print(f"Loading cube shortIDs from: {INPUT_SHORT_IDS_FILE}")
        with open(input_file, 'r') as f:
            short_ids = json.load(f)

        print(f"Found {len(short_ids)} cube shortIDs")
        print(f"Fetching cube data (rate limited to 2 requests/second)...\n")

        success_count = 0
        start_time = time.time()

        for i, cube_id in enumerate(short_ids, 1):
            print(f"[{i}/{len(short_ids)}] {cube_id}")
            if fetch_cube_data(cube_id, headers, output_dir):
                success_count += 1

            # Rate limiting: wait before next request (except for the last one)
            if i < len(short_ids):
                time.sleep(RATE_LIMIT_DELAY)

        elapsed_time = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"Successfully fetched: {success_count}/{len(short_ids)} cubes")
        print(f"Total time: {elapsed_time:.1f} seconds")
        print(f"Data saved to: {output_dir}/")
    else:
        print(f"Input file not found: {INPUT_SHORT_IDS_FILE}")
        print("Run inspect_search.py first to generate the shortIDs file.")

    print("\nDone!")


if __name__ == '__main__':
    main()
