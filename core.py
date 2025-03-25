import requests
import json
import os
import base64
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from typing import List, Any, Dict, Optional, Protocol, TypedDict, Union
from enum import Enum

class LogoData(TypedDict, total=False):
    found: bool
    format: Optional[str]  # 'svg', 'png', etc.
    url: Optional[str]
    data: Optional[str]
    base64: Optional[str]

class PartnerData(TypedDict):
    name: str
    logo_url: str
    full_url: Optional[str]

class PartnersData(TypedDict):
    count: int
    partners: List[PartnerData]

# Protocol definitions for extractors
class NameExtractor(Protocol):
    def __call__(self, soup: BeautifulSoup) -> str: ...

class LogoExtractor(Protocol):
    def __call__(self, soup: BeautifulSoup) -> LogoData: ...

class PartnersExtractor(Protocol):
    def __call__(self, soup: BeautifulSoup) -> PartnersData: ...

def validate_logo_data(data: Dict) -> LogoData:
    result: LogoData = {
        "found": data.get("found", False)
    }
    
    if "format" in data:
        result["format"] = data["format"]
    if "url" in data:
        result["url"] = data["url"]
    if "data" in data:
        result["data"] = data["data"]
    if "base64" in data:
        result["base64"] = data["base64"]
    
    return result

def validate_partners_data(data: Dict) -> PartnersData:
    validated_partners = []
    
    for partner in data.get("partners", []):
        validated_partner: PartnerData = {
            "name": partner.get("name", "unknown"),
            "logo_url": partner.get("logo_url", "")
        }
        if "full_url" in partner:
            validated_partner["full_url"] = partner["full_url"]
        
        validated_partners.append(validated_partner)
    
    return {
        "count": len(validated_partners),
        "partners": validated_partners
    }

class AttributeType(Enum):
    NAME = "name"
    LOGO = "logo"
    PARTNERS = "partners"

class Attribute:
    def __init__(self, name: str, attribute_type: AttributeType, 
                 scraper_function: Union[NameExtractor, LogoExtractor, PartnersExtractor]):
        self.name = name
        self.attribute_type = attribute_type
        self.scraper_function = scraper_function
    
    def extract(self, soup: BeautifulSoup) -> Any:
        result = self.scraper_function(soup)
        
        if self.attribute_type == AttributeType.LOGO:
            return validate_logo_data(result)
        elif self.attribute_type == AttributeType.PARTNERS:
            return validate_partners_data(result)
        
        return result

class Site:
    def __init__(self, name: str, url: str, attributes: List[Attribute], base_url: str = None):
        self.name = name
        self.url = url
        self.attributes = attributes
        self.base_url = base_url or url  # Use provided base_url or fall back to url
        self._results = {}
    
    def scrape(self, request_adapter=None):
        if request_adapter is None:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            }
            try:
                response = requests.get(self.url, headers=headers)
                if response.status_code != 200:
                    print(f"Error: Failed to fetch {self.url}, status code: {response.status_code}")
                    return self
                html_content = response.text
            except Exception as e:
                print(f"Error fetching {self.url}: {e}")
                return self
        else:
            html_content = request_adapter(self.url)
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        for attr in self.attributes:
            try:
                result = attr.extract(soup)
                self._results[attr.name] = result
                print(f"Extracted {attr.name} from {self.name}")
            except Exception as e:
                print(f"Error extracting {attr.name} from {self.name}: {e}")
                self._results[attr.name] = None
        
        return self
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "url": self.url,
            "base_url": self.base_url,
            "data": self._results
        }
    
    def __str__(self) -> str:
        return f"Site(name='{self.name}', results={self._results})"

def download_file(url: str, save_path: str, headers=None) -> bool:
    if not headers:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
        
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to download {url}, status code: {response.status_code}")
            return False
            
        with open(save_path, 'wb') as f:
            f.write(response.content)
            
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def save_base64_to_file(base64_data: str, save_path: str, is_text=False) -> bool:
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        if is_text:
            data = base64.b64decode(base64_data).decode('utf-8')
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(data)
        else:
            data = base64.b64decode(base64_data)
            with open(save_path, 'wb') as f:
                f.write(data)
                
        return True
    except Exception as e:
        print(f"Error saving base64 data to {save_path}: {e}")
        return False

def process_logo_files(site_name: str, logo_data: LogoData) -> LogoData:
    """Process and save logo files, update logo data with file paths"""
    if not logo_data or not logo_data.get("found", False):
        return logo_data
        
    result = dict(logo_data)
    
    site_slug = site_name.lower().replace(' ', '_')
    save_dir = f"data/logos/{site_slug}"
    os.makedirs(save_dir, exist_ok=True)
    
    # Process SVG
    if logo_data.get("format") == "svg" and (logo_data.get("data") or logo_data.get("base64")):
        svg_path = f"{save_dir}/logo.svg"
        
        # Save from base64 or data
        if "base64" in logo_data:
            if save_base64_to_file(logo_data["base64"], svg_path):
                result["svg_file"] = svg_path
        elif "data" in logo_data:
            with open(svg_path, 'w', encoding='utf-8') as f:
                f.write(logo_data["data"])
            result["svg_file"] = svg_path
    
    # Process image URL
    if "url" in logo_data:
        url = logo_data["url"]
        ext = get_file_extension(url)
        image_path = f"{save_dir}/logo.{ext}"
        
        if download_file(url, image_path):
            result[f"{ext}_file"] = image_path
    
    return result

def get_file_extension(url: str) -> str:
    if url.endswith('.svg'):
        return 'svg'
    elif url.endswith('.png'):
        return 'png'
    elif url.endswith('.jpg') or url.endswith('.jpeg'):
        return 'jpg'
    else:
        return 'png'

def resolve_url(url: str, base_url: str = None) -> str:
    if not base_url or '://' in url:
        return url
    return urljoin(base_url, url)

def process_partner_files(site_name: str, partners_data: PartnersData, base_url: str = None) -> PartnersData:
    if not partners_data or not partners_data.get("partners"):
        return partners_data
        
    site_slug = site_name.lower().replace(' ', '_')
    save_dir = f"data/partners/{site_slug}"
    os.makedirs(save_dir, exist_ok=True)
    
    result = dict(partners_data)
    processed_partners = []
    
    for partner in partners_data["partners"]:
        processed_partner = dict(partner)
        
        if logo_url := partner.get("logo_url"):
            name = partner.get("name", "unknown")
            
            # Resolve URL (handle relative URLs)
            full_url = partner.get("full_url") or resolve_url(logo_url, base_url)
            if full_url != logo_url:
                processed_partner["full_url"] = full_url
            
            # Download and save the logo
            ext = get_file_extension(logo_url)
            file_path = f"{save_dir}/{name}.{ext}"
            
            if download_file(full_url, file_path):
                processed_partner["logo_file"] = file_path
        
        processed_partners.append(processed_partner)
    
    result["partners"] = processed_partners
    return result

def save_sites_to_json(sites: List[Site], filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    processed_data = []
    for site in sites:
        site_dict = site.to_dict()
        
        # Process logo files
        if "company_logo" in site_dict["data"]:
            site_dict["data"]["company_logo"] = process_logo_files(
                site_dict["name"],
                site_dict["data"]["company_logo"]
            )
        
        # Process partner files
        if "partners" in site_dict["data"]:
            site_dict["data"]["partners"] = process_partner_files(
                site_dict["name"],
                site_dict["data"]["partners"],
                site_dict.get("base_url")
            )
        
        processed_data.append(site_dict)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, indent=2, ensure_ascii=False)
    
    print(f"Data saved to {filepath}")
