"""
Simple script to inspect and dump the contents of a CubeCobra cube page.
Extracts window.ReactProps from the page which contains all the cube data.
"""

import json
import re
import requests
from bs4 import BeautifulSoup

# Configuration
CUBE_ID = '1fdv1'
URL = f'https://cubecobra.com/cube/overview/{CUBE_ID}'
OUTPUT_HTML = f'output_{CUBE_ID}.html'
OUTPUT_REACT_PROPS = f'output_{CUBE_ID}_react_props.json'

def extract_react_props(html_content):
    """Extract window.ReactProps from the HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all script tags in the body
    scripts = soup.find('body').find_all('script')

    for script in scripts:
        if script.string and 'window.ReactProps' in script.string:
            # Extract the JSON object assigned to window.ReactProps
            # Pattern: window.ReactProps = {...};
            match = re.search(r'window\.ReactProps\s*=\s*(\{.*?\});', script.string, re.DOTALL)
            if match:
                json_str = match.group(1)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    print(f"Error parsing ReactProps JSON: {e}")
                    return None

    return None

def main():
    print(f"Fetching: {URL}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    # Fetch the page
    response = requests.get(URL, headers=headers)
    response.raise_for_status()

    print(f"Status: {response.status_code}")
    print(f"Content-Length: {len(response.content)} bytes")

    # Save raw HTML
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(response.text)
    print(f"\nSaved HTML to: {OUTPUT_HTML}")

    # Extract ReactProps
    print("\nExtracting window.ReactProps...")
    react_props = extract_react_props(response.text)

    if react_props:
        # Save ReactProps as JSON
        with open(OUTPUT_REACT_PROPS, 'w', encoding='utf-8') as f:
            json.dump(react_props, f, indent=2)
        print(f"Saved ReactProps to: {OUTPUT_REACT_PROPS}")

        # Print summary of what we found
        print(f"\nReactProps structure:")
        print(f"  Top-level keys: {list(react_props.keys())}")

        # Print some interesting info if available
        if 'cube' in react_props:
            cube = react_props['cube']
            print(f"\nCube info:")
            print(f"  Name: {cube.get('name')}")
            print(f"  Owner: {cube.get('owner')}")
            print(f"  Card count: {cube.get('card_count')}")

        if 'cards' in react_props:
            print(f"\nCards: {len(react_props['cards'])} found")
    else:
        print("WARNING: Could not find window.ReactProps in the page")

    print("\nDone!")

if __name__ == '__main__':
    main()
