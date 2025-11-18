"""
Simple script to inspect and dump the contents of a CubeCobra cube page.
"""

import json
import requests
from bs4 import BeautifulSoup

# Configuration
CUBE_ID = '1fdv1'
URL = f'https://cubecobra.com/cube/overview/{CUBE_ID}'
OUTPUT_HTML = f'output_{CUBE_ID}.html'
OUTPUT_JSON = f'output_{CUBE_ID}.json'

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

    # Parse with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract some basic info
    info = {
        'url': URL,
        'title': soup.title.string if soup.title else None,
        'meta_tags': {},
    }

    for meta in soup.find_all('meta'):
        if meta.get('name'):
            info['meta_tags'][meta.get('name')] = meta.get('content')
        elif meta.get('property'):
            info['meta_tags'][meta.get('property')] = meta.get('content')

    # Save raw HTML
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(response.text)
    print(f"\nSaved HTML to: {OUTPUT_HTML}")

    # Save parsed info as JSON
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2)
    print(f"Saved info to: {OUTPUT_JSON}")

    # Print summary
    print(f"\nPage Title: {info['title']}")
    print(f"Meta Tags: {len(info['meta_tags'])} found")

    print("\nDone!")

if __name__ == '__main__':
    main()
