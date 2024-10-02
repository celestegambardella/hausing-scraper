#!/usr/bin/env python
from pprint import pprint

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime
import json
import os

# Define base directories
# BASE_DIR = os.getcwd()
# OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
# JSON_FILE_PATH = os.path.join(OUTPUT_DIR, 'houses.json')
# MD_FILE_PATH = os.path.join(OUTPUT_DIR, 'hausing-scraper.md')
OUTPUT_DIR = "src/output/"
JSON_FILE_PATH = OUTPUT_DIR + "houses.json"
MD_FILE_PATH = OUTPUT_DIR + "hausing-scraper.md"

def get_addresses(address_divs):
    addresses = []
    if address_divs:
        for idx, address_div in enumerate(address_divs, start=1):
            # print(f"Address {idx}:", address_div.get_text(strip=True))
            addresses.append(address_div.get_text(strip=True))
    else:
        print("No divs with class 'address' found.")

    return addresses


def get_prices(price_paragraphs):
    prices = []

    # Filter out the numeric price paragraphs
    for price in price_paragraphs:
        text = price.get_text(strip=True)
        # Remove currency symbols and commas
        cleaned_price = ''.join(filter(str.isdigit, text))
        if cleaned_price:
            prices.append(cleaned_price)

    return prices


def create_property_urls(hostname, houses):
    urls = []

    base_url = "https://" + hostname + "/properties-for-rent-amsterdam/"
    for house in houses:
        url = base_url + house.lower().replace(" ", "-").replace(",", "")
        urls.append(url)

    return urls


def get_house_status(house_availability):
    statues = []
    if house_availability:
        for idx, status in enumerate(house_availability, start=1):
            # print(f"Address {idx}:", address_div.get_text(strip=True))
            statues.append(status.get_text(strip=True))
    else:
        print("No divs with class 'availability-caption-2' found.")

    return statues


def get_houses(url, max_price):
    houses = {}
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all divs with class "address"
        address_divs = soup.find_all('div', class_='address')

        # Find all p elements with class "availability-caption-2 text-gray availability"
        house_availability = soup.find_all('p', class_='availability-caption-2')

        # Find all p elements with class "price-text-small-5"
        price_paragraphs = soup.find_all('p', class_='price-text-small-5')

        # Get all addresses
        addresses = get_addresses(address_divs)

        # Get all prices
        price_values = get_prices(price_paragraphs)

        # Get all statuses
        statues = get_house_status(house_availability)

        # Get all urls
        hostname = urlparse(url).netloc
        urls = create_property_urls(hostname, addresses)

        # Check if the number of addresses and prices match
        if len(addresses) == len(price_values):
            for idx, (address, price, status, url) in enumerate(zip(addresses, price_values, statues, urls), start=1):
                if int(price) < max_price and status == "Available":
                    # Construct the dict with houses available
                    houses[address] = {
                        "price": int(price),
                        "url": url,
                        "status": status,
                    }
        else:
            print("The number of addresses and prices do not match.")

    except requests.RequestException as e:
        print(f"An error occurred: {e}")

    return houses


def load_existing_houses(file_name='houses.json'):
    if os.path.exists(file_name):
        with open(file_name, 'r') as fp:
            try:
                return json.load(fp)
            except json.JSONDecodeError:
                print("Error reading the JSON file.")
                return {}
    else:
        return {}


def update_markdown(new_houses, existing_data, md_file_path=MD_FILE_PATH):
    # Ensure the output directory exists
    output_dir = os.path.dirname(md_file_path)
    os.makedirs(output_dir, exist_ok=True)

    with open(md_file_path, 'w') as md_file:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        md_file.write(f"---\n")
        md_file.write(f"title: Hausing Scraper\n")
        md_file.write(f"publishDate: {now}\n")
        md_file.write(f"img: /assets/stock-2.jpg\n")
        md_file.write(f"img_alt: A bright pink sheet of paper used to wrap flowers curves in front of rich blue background\n")
        md_file.write(f"description: |\n")
        md_file.write(f"  Python script that runs hourly and scrapes www.hausing.com for any new properties.\n")
        md_file.write(f"tags:\n  - Dev\n  - Frontend\n  - Scripting\n")
        md_file.write(f"---\n")

        short_time = datetime.now().strftime('%b %d %Y %H:%M')
        if new_houses:
            md_file.write(f"\n### [New] Apartments\n")
            for address, details in new_houses.items():
                md_file.write(f"- **{address}**: €{details['price']}/month - [View Property]({details['url']})\n")
        else:
            md_file.write(f"\n## No New Listings Found\n")

        md_file.write(f"---\n`{short_time}`")
        md_file.write(f"\n###### [Source Code](https://github.com/celestegambardella/hausing-scraper)\n")


def update_houses(new_data, json_file_path=JSON_FILE_PATH, output_file_path=MD_FILE_PATH):
    # Ensure the output directory exists
    output_dir = os.path.dirname(output_file_path)
    os.makedirs(output_dir, exist_ok=True)

    try:
        with open(json_file_path, 'r') as fp:
            existing_data = json.load(fp)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = {}

    # Find new houses by checking if the address exists in the current data
    new_houses = {addr: details for addr, details in new_data.items() if addr not in existing_data}

    print(f"Found {len(new_houses)} new houses:")
    for address, details in new_houses.items():
        print(f"New Appartment: {address}, Price: {details['price']}, URL: {details['url']}")

    # Update existing data with new houses
    existing_data.update(new_houses)
    update_markdown(new_houses, existing_data)

    print("Markdown and JSON files updated with new listings.")

    # Write the updated data back to the JSON file
    # Update the JSON file regardless of new data
    existing_data.update(new_houses)
    with open(json_file_path, 'w') as fp:
        json.dump(existing_data, fp, indent=4)


def main():
    # print("Current Working Directory:", BASE_DIR)
    print("Output Directory:", OUTPUT_DIR)
    print("Output Directory:", JSON_FILE_PATH)
    print("Output Directory:", MD_FILE_PATH)

    url = "https://www.hausing.com/properties-for-rent-amsterdam?sort-asc=price"
    max_price = 2650
    new_houses = get_houses(url, max_price)

    if new_houses:
        update_houses(new_houses)
    else:
        print("No houses found within the price range.")


if __name__ == "__main__":
    main()