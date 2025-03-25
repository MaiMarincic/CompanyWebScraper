from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote
import base64
from typing import List

from core import (
    Attribute, AttributeType, Site, 
    LogoData, PartnersData, PartnerData,
    NameExtractor, LogoExtractor, PartnersExtractor
)

class ScaleNameExtractor(NameExtractor):
    def __call__(self, soup: BeautifulSoup) -> str:
        name_element = soup.find(['h2'])
        return name_element.get_text(strip=True) if name_element else "Scale"

class ScaleLogoExtractor(LogoExtractor):
    def __call__(self, soup: BeautifulSoup) -> LogoData:
        svg_tag = soup.find('svg', class_='w-auto h-full fill-current text-white')
        
        if not svg_tag:
            return LogoData(found=False)
        
        svg_str = str(svg_tag)
        return LogoData(
            found=True,
            format="svg",
            data=svg_str,
            base64=base64.b64encode(svg_str.encode('utf-8')).decode('utf-8')
        )

class ScalePartnersExtractor(PartnersExtractor):
    def __call__(self, soup: BeautifulSoup) -> PartnersData:
        partner_elements = soup.find_all('li', class_=['flex', 'justify-center', 'items-center'])
        
        partner_urls = []
        for li in partner_elements:
            img = li.find('img')
            if img and img.get('src'):
                partner_urls.append(img.get('src'))
        
        # Remove last 3 if they're not actual partners (based on previous logic)
        if len(partner_urls) > 3:
            partner_urls = partner_urls[:-3]
        
        partners: List[PartnerData] = []
        unique_names = set()
        
        for url in partner_urls:
            try:
                parsed = urlparse(url)
                query = parse_qs(parsed.query)
                image_path = query.get('url', [''])[0]
                decoded_path = unquote(image_path)
                
                name = decoded_path.split('/')[-1].replace('.png', '')
                if name in unique_names:
                    continue
                
                unique_names.add(name)
                
                full_url = f"https://scale.com{url}" if url.startswith('/') else url
                
                partners.append(PartnerData(
                    name=name,
                    logo_url=url,
                    full_url=full_url
                ))
            except Exception as e:
                print(f"Error parsing partner URL {url}: {e}")
        
        return PartnersData(
            count=len(partners),
            partners=partners
        )

name_extractor = ScaleNameExtractor()
logo_extractor = ScaleLogoExtractor()
partners_extractor = ScalePartnersExtractor()

scale_site = Site(
    name="Scale AI",
    url="https://scale.com/",
    attributes=[
        Attribute("company_name", AttributeType.NAME, name_extractor),
        Attribute("company_logo", AttributeType.LOGO, logo_extractor),
        Attribute("partners", AttributeType.PARTNERS, partners_extractor)
    ]
)

if __name__ == "__main__":
    scale_site.scrape()
    print(scale_site)
