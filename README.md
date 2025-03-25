AI Company Website Scraper
A flexible, modular framework for scraping AI company websites with a focus on long-term extensibility and scalability.
What It Does
This scraper extracts and organizes key information from company websites:

Company name (included as an example of the attribute system)
Company logo (in original format: SVG, PNG, etc.)
Partner companies (names and logos)

All data is downloaded, properly organized, and packed into a structured JSON file for easy access.

## Overview

This tool provides a clean, object-oriented approach to web scraping with a focus on:
- **Modularity/Extensibility**: Using a dependency injection pattern to easily add new extractors
- **Type Safety**: Comprehensive typing with TypedDict and Protocol definitions
- **Data Persistence**: Saves both structured data (JSON) and media assets (SVG/PNG)

## Currently Supported Websites

- [Scale.com](https://scale.com/) - Scale AI
- [11x.ai](https://www.11x.ai/) - 11X 
- [Webflow.com](https://webflow.com/) - Webflow

## Installation Guide

### Prerequisites

- Python 3.7 or higher

### Setup Instructions

1. **Clone the repository**

```bash
git clone git@github.com:MaiMarincic/CompanyWebScraper.git
```

2. **Create a virtual environment (optional but recommended)**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the main script to scrape all configured websites:

```bash
python main.py
```

### Output Locations

- **JSON Data**: `data/data.json`
- **Company Logos**: `data/logos/{company_name}/logo.{svg|png}`
- **Partner Logos**: `data/partners/{company_name}/{partner_name}.{svg|png}`

## Project Structure

```
.
├── company/               # Company-specific scraper implementations
│   ├── elevenx.py         # Scraper for 11X
│   ├── scale.py           # Scraper for Scale AI
│   └── webflow.py         # Scraper for Webflow
├── core.py                # Core framework definitions
├── main.py                # Main execution script
├── data/                  # Output data directory
│   ├── data.json          # Consolidated results
│   ├── logos/             # Extracted company logos
│   └── partners/          # Extracted partner logos
```

## Key Components

### Attribute System

The framework uses an attribute-based approach to specify what to extract:

- **Name Attribute**: Extract company names
- **Logo Attribute**: Extract and process company logos
- **Partners Attribute**: Extract company partners and their logos

### Extractors

Each attribute has an associated extractor that implements the actual scraping logic:

- `NameExtractor`: Extracts company name
- `LogoExtractor`: Extracts logo information (URLs, formats, etc.)
- `PartnersExtractor`: Extracts partner information

## Extending the Scraper

### Adding a New Website

1. Create a new file in the `company/` directory (e.g., `company/newcomp.py`)
2. Define extractor classes for each attribute you want to scrape:

```python
from bs4 import BeautifulSoup
from core import (
    Attribute, AttributeType, Site, 
    LogoData, PartnersData, PartnerData,
    NameExtractor, LogoExtractor, PartnersExtractor
)

class NewCompanyNameExtractor(NameExtractor):
    def __call__(self, soup: BeautifulSoup) -> str:
        # Your extraction logic here
        return name

class NewCompanyLogoExtractor(LogoExtractor):
    def __call__(self, soup: BeautifulSoup) -> LogoData:
        # Your extraction logic here
        return {
            "found": True,
            "format": "svg",  # or "png", etc.
            "url": logo_url
        }

class NewCompanyPartnersExtractor(PartnersExtractor):
    def __call__(self, soup: BeautifulSoup) -> PartnersData:
        # Your extraction logic here
        return {
            "count": len(partners),
            "partners": partners  # List of dicts with "name" and "logo_url"
        }

# Create extractor instances
name_extractor = NewCompanyNameExtractor()
logo_extractor = NewCompanyLogoExtractor()
partners_extractor = NewCompanyPartnersExtractor()

# Define site
newcomp_site = Site(
    name="New Company",
    url="https://newcomp.com/",
    attributes=[
        Attribute("company_name", AttributeType.NAME, name_extractor),
        Attribute("company_logo", AttributeType.LOGO, logo_extractor),
        Attribute("partners", AttributeType.PARTNERS, partners_extractor)
    ]
)
```

3. Import and add the site to the list in `main.py`:

```python
from company.newcomp import newcomp_site

# In the main function:
sites = [
    scale_site,
    elevenx_site,
    webflow_site,
    newcomp_site  # Add your new site
]
```
