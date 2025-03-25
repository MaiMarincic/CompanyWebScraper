from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
from typing import List

from core import (
    Attribute, AttributeType, Site, 
    LogoData, PartnersData, PartnerData,
    NameExtractor, LogoExtractor, PartnersExtractor
)

class ElevenXNameExtractor(NameExtractor):
    def __call__(self, soup: BeautifulSoup) -> str:
        title_tag = soup.find('title')
        if not title_tag:
            return "11X"
        return title_tag.text.strip()

class ElevenXLogoExtractor(LogoExtractor):
    def __call__(self, soup: BeautifulSoup) -> LogoData:
        logo_tag = soup.find("img", {"class": "_11x-logo"})
        
        if not logo_tag or not logo_tag.get('src'):
            return {"found": False}
        
        logo_url = logo_tag['src']
        format_type = "svg" if logo_url.endswith('.svg') else "png"
        
        return LogoData(
            found=True,
            format=format_type,
            url=logo_url
        )

class ElevenXPartnersExtractor(PartnersExtractor):
    def __call__(self, soup: BeautifulSoup) -> PartnersData:
        partner_wrappers = soup.find_all(class_='logo3_wrapper')
        
        partners: List[PartnerData] = []
        unique_names = set()
        
        for wrapper in partner_wrappers:
            img = wrapper.find('img')
            if not img or not img.get('src'):
                continue
                
            img_url = img.get('src')
            if not img_url.endswith('.svg'):
                continue
                
            filename = urlparse(img_url).path.split('/')[-1]
            name_part = filename.replace('.svg', '')
            
            parts = re.split(r'[_\-]', name_part)
            company_parts = parts[1:] if len(parts) > 1 else parts
            company_name = '_'.join(company_parts).lower()
            
            company_name = re.sub(r'\W+', '', company_name)
            
            if company_name in unique_names:
                continue
                
            unique_names.add(company_name)
            
            partners.append({
                "name": company_name,
                "logo_url": img_url
            })
        
        return PartnersData(
            count=len(partners),
            partners=partners
        )

name_extractor = ElevenXNameExtractor()
logo_extractor = ElevenXLogoExtractor()
partners_extractor = ElevenXPartnersExtractor()

elevenx_site = Site(
    name="11X",
    url="https://www.11x.ai/",
    attributes=[
        Attribute("company_name", AttributeType.NAME, name_extractor),
        Attribute("company_logo", AttributeType.LOGO, logo_extractor),
        Attribute("partners", AttributeType.PARTNERS, partners_extractor)
    ]
)

if __name__ == "__main__":
    elevenx_site.scrape()
    print(elevenx_site)
