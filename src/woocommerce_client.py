from typing import List, Dict, Optional
from woocommerce import API
from tenacity import retry, stop_after_attempt, wait_exponential
import math

from .config import config, SiteConfig


class WooCommerceClient:
    def __init__(self, site_config: Optional[SiteConfig] = None):
        # Use provided site config or fall back to default
        if site_config:
            url = str(site_config.url)
            consumer_key = site_config.consumer_key
            consumer_secret = site_config.consumer_secret
        else:
            url = str(config.woocommerce.url)
            consumer_key = config.woocommerce.consumer_key
            consumer_secret = config.woocommerce.consumer_secret
            
        self.api = API(
            url=url,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            version="wc/v3",
            timeout=config.crawler.timeout_seconds
        )
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_all_products(self, per_page: int = 100) -> List[Dict]:
        """Fetch all products from WooCommerce"""
        products = []
        page = 1
        
        while True:
            response = self.api.get("products", params={
                "per_page": per_page,
                "page": page,
                "status": "publish"
            })
            
            if response.status_code != 200:
                print(f"Error fetching products: {response.text}")
                break
                
            batch = response.json()
            if not batch:
                break
                
            products.extend(batch)
            
            # Check if there are more pages
            total_pages = int(response.headers.get('X-WP-TotalPages', 1))
            if page >= total_pages:
                break
                
            page += 1
            
        return products
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Fetch a single product by ID"""
        try:
            response = self.api.get(f"products/{product_id}")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching product {product_id}: {e}")
        return None
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_all_categories(self) -> List[Dict]:
        """Fetch all product categories"""
        categories = []
        page = 1
        
        while True:
            response = self.api.get("products/categories", params={
                "per_page": 100,
                "page": page
            })
            
            if response.status_code != 200:
                print(f"Error fetching categories: {response.text}")
                break
                
            batch = response.json()
            if not batch:
                break
                
            categories.extend(batch)
            
            total_pages = int(response.headers.get('X-WP-TotalPages', 1))
            if page >= total_pages:
                break
                
            page += 1
            
        return categories
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_shipping_zones(self) -> List[Dict]:
        """Fetch all shipping zones with their methods and locations"""
        zones = []
        
        response = self.api.get("shipping/zones")
        if response.status_code == 200:
            zones = response.json()
            
            # Get methods and locations for each zone
            for zone in zones:
                zone_id = zone.get('id')
                
                # Get methods for this zone
                methods_response = self.api.get(f"shipping/zones/{zone_id}/methods")
                if methods_response.status_code == 200:
                    zone['methods'] = methods_response.json()
                
                # Get locations for this zone
                locations_response = self.api.get(f"shipping/zones/{zone_id}/locations")
                if locations_response.status_code == 200:
                    zone['locations'] = locations_response.json()
                    
        return zones
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_shipping_classes(self) -> List[Dict]:
        """Fetch all shipping classes"""
        classes = []
        
        response = self.api.get("products/shipping_classes")
        if response.status_code == 200:
            classes = response.json()
            
        return classes
    
    def get_product_variations(self, product_id: int) -> List[Dict]:
        """Fetch all variations for a variable product"""
        variations = []
        page = 1
        
        while True:
            response = self.api.get(f"products/{product_id}/variations", params={
                "per_page": 100,
                "page": page
            })
            
            if response.status_code != 200:
                break
                
            batch = response.json()
            if not batch:
                break
                
            variations.extend(batch)
            
            total_pages = int(response.headers.get('X-WP-TotalPages', 1))
            if page >= total_pages:
                break
                
            page += 1
            
        return variations