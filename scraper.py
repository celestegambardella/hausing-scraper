#!/usr/bin/env python
import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime
import zoneinfo

# Define base directories
BASE_DIR = os.getcwd()
OUTPUT_DIR = os.path.join(BASE_DIR, "output/")
JSON_FILE_PATH = os.path.join(OUTPUT_DIR, "listings.json")
MD_FILE_PATH = os.path.join(OUTPUT_DIR, "hausing-scraper.md")

def extract_elements(elements, key):
    """Extracts text from HTML elements and returns them as a list."""
    values = [element.get_text(strip=True) for element in elements]
    if not values:
        print(f"No elements found for '{key}'.")
    return values

def get_bedrooms(elements):
    """Extracts bedroom information from elements."""
    return [block.find('div', class_='sqm-space-right').get_text(strip=True)
            for block in elements
            if block.find('div', class_='sqm-space-right')]

def extract_prices(price_paragraphs):
    """Extracts prices from price paragraph elements."""
    prices = []
    for price in price_paragraphs:
        text = price.get_text(strip=True)
        # Remove currency symbols and commas
        cleaned_price = ''.join(filter(str.isdigit, text))
        if cleaned_price:
            prices.append(cleaned_price)
    return prices

def create_property_urls(hostname, houses):
    """Creates property URLs based on a hostname and house names."""
    base_url = f"https://{hostname}/properties-for-rent-amsterdam/"
    return [base_url + house.lower().replace(" ", "-").replace(",", "") for house in houses]

def get_listings(url, max_price):
    """Scrapes the property listings from the specified URL."""
    listings = {}
    google_maps = "http://maps.google.com/?q="
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Get all addresses
        addresses = extract_elements(soup.find_all('div', class_='address'), "address")
        # Get all prices
        prices = extract_prices(soup.find_all('p', class_='price-text-small-5'))
        # Get all statuses
        statuses = extract_elements(soup.find_all('p', class_='availability-caption-2'), "status")
        # Get all bedrooms
        bedroom_nums = get_bedrooms(soup.find_all('div', class_='post-meta-left'))
        hostname = urlparse(url).netloc
        urls = create_property_urls(hostname, addresses)

        # Ensure all data is aligned
        if len(addresses) == len(prices):
            listings = {
                address: {
                    "price": int(price),
                    "url": url,
                    "status": status,
                    "beds": bed_num,
                    "google_maps": f"{google_maps}{address.replace(' ', '-')}"
                }
                for address, price, status, url, bed_num in zip(addresses, prices, statuses, urls, bedroom_nums)
                if int(price) < max_price and status == "Available" and int(bed_num) == 2
            }
        else:
            print("Mismatch in the number of addresses and prices.")
    except requests.RequestException as e:
        print(f"An error occurred: {e}")

    return listings

def load_existing_listings(file_name=JSON_FILE_PATH):
    """Loads existing listings from a JSON file, creating it if it doesn't exist."""
    if not os.path.exists(file_name):
        # Create the file with an empty dictionary
        with open(file_name, 'w') as fp:
            json.dump({}, fp)  # Initialize the file with an empty JSON object
        return {}

    try:
        with open(file_name, 'r') as fp:
            return json.load(fp)  # Load and return the existing data
    except json.JSONDecodeError:
        print("Error reading the JSON file.")  # Handle JSON decode errors
        return {}

def write_old_listings(file, data):
    """Writes previously found listings to the markdown file."""
    file.write("\n### Previously Found Listings\n")
    for address, details in data.items():
        price = f"€{details['price']}/month"
        beds = f"Beds: {details['beds']}"
        url = f"[View Property]({details['url']})"
        google_maps = f"[Google Maps]({details['google_maps']})"
        file.write(f"#### {address}\n- {price}\n- {beds}\n- {url}\n- {google_maps}\n")

def update_markdown(new_listings, existing_data):
    """Updates the markdown file with new and old listings."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)  # Ensure the output directory exists
    amsterdam_tz = zoneinfo.ZoneInfo("Europe/Amsterdam")
    current_time = datetime.now(amsterdam_tz).strftime('%Y-%m-%d %H:%M:%S')
    base_url = "https://www.hausing.com/properties-for-rent-amsterdam?sort-asc=price"

    with open(MD_FILE_PATH, 'w') as md_file:
        md_file.write(f"---\n")
        md_file.write(f"title: Housing Scraper\n")
        md_file.write(f"publishDate: {current_time}\n")
        md_file.write(f"img: /assets/stock-1.jpg\n")
        md_file.write(f"img_alt: A collection of dutch houses\n")
        md_file.write(f"description: |\n  Python script that runs hourly and scrapes www.hausing.com for any new properties.\n")
        md_file.write(f"tags:\n  - Dev\n  - Frontend\n  - Scripting\n")
        md_file.write(f"---\n")

        short_time = datetime.now(amsterdam_tz).strftime('%b %d %Y %H:%M')
        if new_listings:
            md_file.write("\n### [New] Listings\n")
            for address, details in new_listings.items():
                price = f"€{details['price']}/month"
                beds = f"Beds: {details['beds']}"
                url = f"[View Property]({details['url']})"
                google_maps = f"[Google Maps]({details['google_maps']})"
                md_file.write(f"#### {address}\n- {price}\n- {beds}\n- {url}\n- {google_maps}\n")
            if existing_data:
                write_old_listings(md_file, existing_data)
        else:
            md_file.write("\n## No New Listings Found\n")
            if existing_data:
                write_old_listings(md_file, existing_data)

        md_file.write(f"---\n###### [`www.hausing.com`]({base_url})\n")
        md_file.write(f"\n`{short_time}`")
        md_file.write(f"\n###### [Source Code](https://github.com/celestegambardella/hausing-scraper)\n")

def update_listings(new_data):
    """Updates the JSON file with new listings."""
    existing_data = load_existing_listings()
    new_listings = {addr: details for addr, details in new_data.items() if addr not in existing_data}

    print(f"Found {len(new_listings)} new listings:")
    for address, details in new_listings.items():
        print(f"New Listing: {address}, Price: {details['price']}, Bedrooms: {details['beds']}, URL: {details['url']}")

    update_markdown(new_listings, existing_data)

    print("Markdown and JSON files updated with new listings.")
    existing_data.update(new_listings)

    # Overwrite the JSON file with updated data
    with open(JSON_FILE_PATH, 'w') as fp:
        json.dump(new_data, fp, indent=4)

def main():
    """Main entry point for the script."""
    print("Current Working Directory:", BASE_DIR)
    print("Output Directory:", OUTPUT_DIR)
    print("Output JSON File:", JSON_FILE_PATH)
    print("Output Markdown File:", MD_FILE_PATH)

    url = "https://www.hausing.com/properties-for-rent-amsterdam?sort-asc=price"
    max_price = 2650
    new_listings = get_listings(url, max_price)

    update_listings(new_listings)

if __name__ == "__main__":
    main()
