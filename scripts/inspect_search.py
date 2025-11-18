"""
Simple script to fetch cube shortIDs from CubeCobra search page.
Extracts shortIDs for later detailed fetching.
"""

import json
import re
import requests
from bs4 import BeautifulSoup

# Configuration
SEARCH_URL = 'https://cubecobra.com/search'
OUTPUT_SHORT_IDS = 'output_cube_short_ids.json'


def extract_react_props(html_content):
    """Extract window.reactProps from the HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all script tags in the body
    body = soup.find('body')
    if not body:
        return None

    scripts = body.find_all('script')

    for script in scripts:
        if script.string and 'window.reactProps' in script.string:
            # Extract the JSON object assigned to window.reactProps
            # Pattern: window.reactProps = {...};
            match = re.search(r'window\.reactProps\s*=\s*(\{.*?\});', script.string, re.DOTALL)
            if match:
                json_str = match.group(1)
                # Replace JavaScript undefined with JSON null
                json_str = re.sub(r'\bundefined\b', 'null', json_str)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    print(f"Error parsing reactProps JSON: {e}")
                    print(f"First 500 chars of JSON: {json_str[:500]}")
                    return None

    return None


def extract_short_ids(react_props):
    """Extract only the shortID from each cube in the cubes array."""
    if not react_props or 'cubes' not in react_props:
        return []

    cubes = react_props.get('cubes', [])
    short_ids = []

    for cube in cubes:
        short_id = cube.get('shortId')
        if short_id:
            short_ids.append(short_id)

    return short_ids


def main():
    print(f"Fetching cube shortIDs from {SEARCH_URL}...")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(SEARCH_URL, headers=headers)
        response.raise_for_status()

        print(f"Status: {response.status_code}")

        # Extract reactProps
        react_props = extract_react_props(response.text)

        if react_props:
            short_ids = extract_short_ids(react_props)
            print(f"Found {len(short_ids)} cubes")

            # Save shortIDs to file
            with open(OUTPUT_SHORT_IDS, 'w', encoding='utf-8') as f:
                json.dump(short_ids, f, indent=2)
            print(f"\nSaved {len(short_ids)} shortIDs to: {OUTPUT_SHORT_IDS}")

            # Print first few examples
            if short_ids:
                print(f"\nFirst 5 shortIDs:")
                for short_id in short_ids[:5]:
                    print(f"  - {short_id}")
        else:
            print("WARNING: Could not find window.reactProps")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")

    print("\nDone!")


if __name__ == '__main__':
    main()
