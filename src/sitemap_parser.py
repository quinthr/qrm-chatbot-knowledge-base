import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import config


class SitemapParser:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.headers = {
            'User-Agent': config.crawler.user_agent
        }
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _fetch_url(self, url: str) -> Optional[str]:
        """Fetch URL content with retry logic"""
        try:
            response = requests.get(
                url, 
                headers=self.headers, 
                timeout=config.crawler.timeout_seconds
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
            
    def parse_sitemap(self, sitemap_url: Optional[str] = None) -> List[Dict[str, str]]:
        """Parse sitemap.xml and return list of URLs with metadata"""
        if not sitemap_url:
            sitemap_url = urljoin(self.base_url, '/sitemap.xml')
            
        urls = []
        content = self._fetch_url(sitemap_url)
        
        if not content:
            return urls
            
        try:
            root = ET.fromstring(content)
            
            # Handle sitemap index (multiple sitemaps)
            if root.tag.endswith('sitemapindex'):
                for sitemap in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
                    loc = sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc is not None and loc.text:
                        # Recursively parse sub-sitemaps
                        urls.extend(self.parse_sitemap(loc.text))
                        time.sleep(config.crawler.delay_seconds)
            else:
                # Regular sitemap
                for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                    loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    lastmod = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
                    priority = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}priority')
                    
                    if loc is not None and loc.text:
                        url_data = {
                            'url': loc.text,
                            'lastmod': lastmod.text if lastmod is not None else None,
                            'priority': priority.text if priority is not None else '0.5'
                        }
                        urls.append(url_data)
                        
        except ET.ParseError as e:
            print(f"Error parsing sitemap XML: {e}")
            
        return urls
    
    def categorize_urls(self, urls: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
        """Categorize URLs by type (product, category, page, etc.)"""
        categorized = {
            'products': [],
            'categories': [],
            'pages': [],
            'posts': [],
            'other': []
        }
        
        for url_data in urls:
            url = url_data['url']
            
            if '/product/' in url or '/shop/' in url:
                categorized['products'].append(url_data)
            elif '/product-category/' in url or '/category/' in url:
                categorized['categories'].append(url_data)
            elif '/page/' in url or url.endswith('/about/') or url.endswith('/contact/'):
                categorized['pages'].append(url_data)
            elif '/blog/' in url or '/post/' in url:
                categorized['posts'].append(url_data)
            else:
                categorized['other'].append(url_data)
                
        return categorized