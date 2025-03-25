from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
from typing import List

from core import (
    Attribute, AttributeType, Site, 
    LogoData, PartnersData, PartnerData,
    NameExtractor, LogoExtractor, PartnersExtractor
)

class WebflowNameExtractor(NameExtractor):
    def __call__(self, soup: BeautifulSoup) -> str:
        title_tag = soup.find('title')
        if not title_tag:
            return "Webflow"
        
        title = title_tag.text.strip()
        if " - " in title:
            title = title.split(" - ")[0].strip()
        elif " | " in title:
            title = title.split(" | ")[0].strip()
        
        return title

class WebflowLogoExtractor(LogoExtractor):
    def __call__(self, soup: BeautifulSoup) -> LogoData:
        logo_tag = soup.find("img", {"alt": "Webflow"}) or soup.find("img", {"class": "logo"})
        
        if not logo_tag or not logo_tag.get('src'):
            return LogoData(found=False)
        
        logo_url = logo_tag['src']
        format_type = "svg" if logo_url.endswith('.svg') else "png"
        
        return LogoData(
            found=True,
            format=format_type,
            url=logo_url
        )

class WebflowPartnersExtractor(PartnersExtractor):
    def __call__(self, soup: BeautifulSoup) -> PartnersData:
        logo_wrappers = soup.find_all(class_="logo_wrapper")
        
        partners: List[PartnerData] = []
        unique_names = set()
        
        for wrapper in logo_wrappers:
            img = wrapper.find('img', class_="logo_grid-logos")
            if not img or not img.get('src'):
                continue
                
            img_url = img.get('src')
            alt_text = img.get('alt', '').strip()
            
            if alt_text:
                company_name = alt_text.lower().replace(' ', '_')
            else:
                filename = urlparse(img_url).path.split('/')[-1]
                name_part = filename.split('.')[0]
                
                company_name = name_part.split('_')[-1].lower() if '_' in name_part else name_part.lower()
            
            company_name = re.sub(r'\W+', '_', company_name).strip('_')
            
            if not company_name or company_name in unique_names:
                continue
            
            unique_names.add(company_name)
            
            partners.append(PartnerData(
                name=company_name,
                logo_url=img_url
            ))
        
        return PartnersData(
            count=len(partners),
            partners=partners
        )

name_extractor = WebflowNameExtractor()
logo_extractor = WebflowLogoExtractor()
partners_extractor = WebflowPartnersExtractor()

webflow_site = Site(
    name="Webflow",
    url="https://webflow.com/",
    attributes=[
        Attribute("company_name", AttributeType.NAME, name_extractor),
        Attribute("company_logo", AttributeType.LOGO, logo_extractor),
        Attribute("partners", AttributeType.PARTNERS, partners_extractor)
    ]
)

if __name__ == "__main__":
    webflow_site.scrape()
    print(webflow_site)
