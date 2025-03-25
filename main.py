import os
import sys
from core import save_sites_to_json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from company.scale import scale_site
from company.elevenx import elevenx_site
from company.webflow import webflow_site

def main():
    sites = [
        scale_site,
        elevenx_site,
        webflow_site
    ]
    
    scraped_sites = []
    for site in sites:
        print(f"Scraping {site.name} ({site.url})...")
        site.scrape()
        scraped_sites.append(site)
        print(f"Finished scraping {site.name}")
        print("-" * 40)
    
    output_path = "data/data.json"
    save_sites_to_json(scraped_sites, output_path)
    
    print(f"\nScraped {len(scraped_sites)} sites. Data saved to {output_path}")

if __name__ == "__main__":
    main()
