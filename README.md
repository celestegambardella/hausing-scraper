# Table of Contents
<!-- TOC start (generated with https://github.com/derlin/bitdowntoc) -->

- [Hausing Scraper](#hausing-scraper)
   * [Overview](#overview)
   * [Features](#features)
   * [Requirements](#requirements)
   * [Usage](#usage)
   * [Workflows](#workflows)
      + [1. Production Workflow](#1-production-workflow)
      + [2. Development Workflow](#2-development-workflow)
   * [Upcoming Features](#upcoming-features)
      + [Additional Websites Support](#additional-websites-support)
      + [Filtering Results](#filtering-results)
   * [License](#license)

<!-- TOC end -->


# Hausing Scraper

## Overview

The Hausing Scraper is a Python script designed to scrape rental property listings from Hausing for Amsterdam. It extracts key details about properties such as addresses, prices, statuses, and the number of bedrooms, and outputs this data in both JSON and Markdown formats.

## Features

- Scrapes rental listings from a specified URL.
  - Extracts detailed information:
    - Address
    - Price
    - Availability status
    - Number of bedrooms
    - Google Maps link
  - Outputs data to:
    - [`listings.json`](outputs/listings.json) for structured storage.
    - [`hausing-scraper.md`](outputs/hausing-scraper.md) for human-readable documentation.

## Requirements

- Python 3.x
- Required libraries:
  - requests
  - beautifulsoup4

You can install the required libraries using at the root of the directory:

```bash
pip install -r requirements.txt
```

## Usage
To run the scraper, execute the script:

```bash
python hausing_scraper.py
```

The script will scrape the listings and update the JSON and Markdown files.

## Workflows

### 1. Production Workflow
The Production Workflow is set up to automatically update the housing scraper hourly and can also be triggered manually or on push to the main branch.

- Workflow File: [`.github/workflows/prod.yml`](.github/workflows/prod.yml)

Uses the [`scraper.py`](scraper.py) file to run the script and generare outputs.

#### Outputs

- Updated `hausing-scraper.md` and `listings.json` files
- The `hausing-scraper.md` file is copied over to my personal github.io [page](https://celestegambardella.github.io/work/hausing-scrapper/), commited, pushed, merged, and deployed to the [repo](https://github.com/celestegambardella/celestegambardella.github.io/blob/prod/src/content/work/hausing-scrapper.md) 



### 2. Development Workflow
The Development Workflow is designed for testing updates to the scraper. It triggers on pushes to the dev branch.

Workflow File: [`.github/workflows/dev.yml`](.github/workflows/dev.yml)

#### Outputs

- Updated `hausing-scraper.md` and `listings.json` files
- The `hausing-scraper.md` file is copied over to my personal github.io [page](https://celestegambardella.github.io/work/hausing-scrapper/) but NOT (commited, pushed, merged, and deployed)


## Upcoming Features


### Additional Websites Support

Support other website scraping like http://pararius.com and https://www.funda.nl in results


### Filtering Results

The results right are filtered by max price, if it is available, and how many bedrooms

###### These are static filters for now:
> - Price: Max €2650/mo
> 
> - Beds: 2
> 
> - Listing Status: Available

#### Creating dynamic fields

Client-Side Filtering (After Build)


## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for details.
