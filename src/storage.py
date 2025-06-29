import json
from typing import List, Dict, Optional
from datetime import datetime
import chromadb
from chromadb.utils import embedding_functions
import openai

from .models import (
    Product, ProductVariation, Category, ShippingZone, 
    ShippingMethod, ShippingClass, ShippingClassRate, CrawlLog, Site, get_database_session
)
from .config import config


class DataStorage:
    def __init__(self, site_id: int = None):
        # SQL database session
        db_type = "PostgreSQL" if config.database.is_postgresql else ("MySQL" if config.database.is_mysql else "SQLite")
        print(f"Using database: {db_type}")
        print(f"Database URL: {config.database.url}")
        self.db_session = get_database_session(config.database.url)
        self.site_id = site_id
        
        # ChromaDB for vector storage
        self.chroma_client = chromadb.PersistentClient(
            path=config.database.chroma_persist_directory
        )
        
        # OpenAI embeddings
        openai.api_key = config.openai_api_key
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=config.openai_api_key,
            model_name="text-embedding-ada-002"
        )
        
        # Create or get collections (include site_id in collection name for separation)
        collection_suffix = f"_site_{site_id}" if site_id else ""
        self.products_collection = self.chroma_client.get_or_create_collection(
            name=f"products{collection_suffix}",
            embedding_function=self.embedding_function
        )
        
        self.pages_collection = self.chroma_client.get_or_create_collection(
            name=f"pages{collection_suffix}",
            embedding_function=self.embedding_function
        )
        
    def save_products(self, products_data: List[Dict]) -> int:
        """Save products to database and vector store"""
        if not self.site_id:
            raise ValueError("site_id must be set before saving products")
            
        saved_count = 0
        
        for product_data in products_data:
            try:
                # Check if product exists for this site
                existing = self.db_session.query(Product).filter_by(
                    site_id=self.site_id,
                    woo_id=product_data['id']
                ).first()
                
                if existing:
                    # Update existing product
                    product = existing
                else:
                    # Create new product
                    product = Product()
                    
                # Update product fields
                product.site_id = self.site_id
                product.woo_id = product_data['id']
                product.name = product_data.get('name', '')
                product.slug = product_data.get('slug', '')
                product.permalink = product_data.get('permalink', '')
                product.sku = product_data.get('sku', '')
                product.price = product_data.get('price', '')
                product.regular_price = product_data.get('regular_price', '')
                product.sale_price = product_data.get('sale_price', '')
                product.description = product_data.get('description', '')
                product.short_description = product_data.get('short_description', '')
                product.weight = product_data.get('weight', '')
                
                # Dimensions
                dimensions = product_data.get('dimensions', {})
                product.dimensions_length = dimensions.get('length', '')
                product.dimensions_width = dimensions.get('width', '')
                product.dimensions_height = dimensions.get('height', '')
                
                product.shipping_class = product_data.get('shipping_class', '')
                product.stock_quantity = product_data.get('stock_quantity')
                product.stock_status = product_data.get('stock_status', 'instock')
                product.manage_stock = product_data.get('manage_stock', False)
                product.featured = product_data.get('featured', False)
                
                if not existing:
                    self.db_session.add(product)
                    
                self.db_session.commit()
                
                # Add to vector store
                self._add_product_to_vector_store(product, product_data)
                
                saved_count += 1
                
            except Exception as e:
                print(f"Error saving product {product_data.get('id')}: {e}")
                self.db_session.rollback()
                
        return saved_count
    
    def _add_product_to_vector_store(self, product: Product, product_data: Dict):
        """Add product to ChromaDB vector store"""
        # Create searchable text
        search_text = f"""
        Product: {product.name}
        SKU: {product.sku}
        Price: {product.price}
        Description: {product.description}
        Short Description: {product.short_description}
        Categories: {', '.join([cat.get('name', '') for cat in product_data.get('categories', [])])}
        Tags: {', '.join([tag.get('name', '') for tag in product_data.get('tags', [])])}
        Attributes: {json.dumps(product_data.get('attributes', []))}
        """
        
        metadata = {
            "site_id": str(self.site_id),
            "product_id": str(product.woo_id),
            "name": product.name,
            "sku": product.sku or "",
            "price": product.price or "",
            "permalink": product.permalink or "",
            "in_stock": product.stock_status == "instock",
            "type": "product"
        }
        
        self.products_collection.upsert(
            documents=[search_text],
            metadatas=[metadata],
            ids=[f"site_{self.site_id}_product_{product.woo_id}"]
        )
        
    def save_product_variations(self, product_id: int, variations_data: List[Dict]) -> int:
        """Save product variations to database"""
        if not self.site_id:
            raise ValueError("site_id must be set before saving variations")
            
        saved_count = 0
        
        for variation_data in variations_data:
            try:
                existing = self.db_session.query(ProductVariation).filter_by(
                    site_id=self.site_id,
                    woo_id=variation_data['id']
                ).first()
                
                if existing:
                    variation = existing
                else:
                    variation = ProductVariation()
                    
                variation.site_id = self.site_id
                variation.product_id = product_id
                variation.woo_id = variation_data['id']
                variation.sku = variation_data.get('sku', '')
                variation.price = variation_data.get('price', '')
                variation.regular_price = variation_data.get('regular_price', '')
                variation.sale_price = variation_data.get('sale_price', '')
                variation.stock_quantity = variation_data.get('stock_quantity')
                variation.stock_status = variation_data.get('stock_status', 'instock')
                variation.weight = variation_data.get('weight', '')
                
                # Dimensions
                dimensions = variation_data.get('dimensions', {})
                variation.dimensions_length = dimensions.get('length', '')
                variation.dimensions_width = dimensions.get('width', '')
                variation.dimensions_height = dimensions.get('height', '')
                
                # Store attributes as JSON
                variation.attributes = json.dumps(variation_data.get('attributes', []))
                
                if not existing:
                    self.db_session.add(variation)
                    
                self.db_session.commit()
                saved_count += 1
                
            except Exception as e:
                print(f"Error saving variation {variation_data.get('id')}: {e}")
                self.db_session.rollback()
                
        return saved_count
    
    def save_categories(self, categories_data: List[Dict]) -> int:
        """Save categories to database"""
        if not self.site_id:
            raise ValueError("site_id must be set before saving categories")
            
        saved_count = 0
        
        for category_data in categories_data:
            try:
                existing = self.db_session.query(Category).filter_by(
                    site_id=self.site_id,
                    woo_id=category_data['id']
                ).first()
                
                if existing:
                    category = existing
                else:
                    category = Category()
                    
                category.site_id = self.site_id
                category.woo_id = category_data['id']
                category.name = category_data.get('name', '')
                category.slug = category_data.get('slug', '')
                category.description = category_data.get('description', '')
                category.parent_id = category_data.get('parent', 0) or None
                
                if not existing:
                    self.db_session.add(category)
                    
                self.db_session.commit()
                saved_count += 1
                
            except Exception as e:
                print(f"Error saving category {category_data.get('id')}: {e}")
                self.db_session.rollback()
                
        return saved_count
    
    def save_shipping_data(self, zones_data: List[Dict], classes_data: List[Dict]):
        """Save shipping zones and classes"""
        if not self.site_id:
            raise ValueError("site_id must be set before saving shipping data")
            
        # Save shipping zones
        for zone_data in zones_data:
            try:
                existing = self.db_session.query(ShippingZone).filter_by(
                    site_id=self.site_id,
                    woo_id=zone_data['id']
                ).first()
                
                if existing:
                    zone = existing
                else:
                    zone = ShippingZone()
                    
                zone.site_id = self.site_id
                zone.woo_id = zone_data['id']
                zone.name = zone_data.get('name', '')
                zone.order = zone_data.get('order', 0)
                
                # Clean location data - remove API metadata and keep only essential fields
                locations = zone_data.get('locations', [])
                cleaned_locations = []
                for location in locations:
                    cleaned_location = {
                        'code': location.get('code', ''),
                        'type': location.get('type', '')
                    }
                    cleaned_locations.append(cleaned_location)
                zone.locations = json.dumps(cleaned_locations)
                
                if not existing:
                    self.db_session.add(zone)
                    
                self.db_session.commit()
                
                # Save shipping methods for this zone
                for method_data in zone_data.get('methods', []):
                    self._save_shipping_method(zone.id, method_data)
                    
            except Exception as e:
                print(f"Error saving shipping zone {zone_data.get('id')}: {e}")
                self.db_session.rollback()
                
        # Save shipping classes
        for class_data in classes_data:
            try:
                existing = self.db_session.query(ShippingClass).filter_by(
                    site_id=self.site_id,
                    woo_id=class_data['id']
                ).first()
                
                if existing:
                    shipping_class = existing
                else:
                    shipping_class = ShippingClass()
                    
                shipping_class.site_id = self.site_id
                shipping_class.woo_id = class_data['id']
                shipping_class.name = class_data.get('name', '')
                shipping_class.slug = class_data.get('slug', '')
                shipping_class.description = class_data.get('description', '')
                
                if not existing:
                    self.db_session.add(shipping_class)
                    
                self.db_session.commit()
                
            except Exception as e:
                print(f"Error saving shipping class {class_data.get('id')}: {e}")
                self.db_session.rollback()
                
    def _save_shipping_method(self, zone_id: int, method_data: Dict):
        """Save individual shipping method and its class rates"""
        try:
            existing = self.db_session.query(ShippingMethod).filter_by(
                zone_id=zone_id,
                instance_id=method_data.get('instance_id')
            ).first()
            
            if existing:
                method = existing
            else:
                method = ShippingMethod()
                
            method.site_id = self.site_id
            method.zone_id = zone_id
            method.instance_id = method_data.get('instance_id')
            method.title = method_data.get('title', '')
            method.method_id = method_data.get('method_id', '')
            method.method_title = method_data.get('method_title', '')
            method.enabled = method_data.get('enabled', True)
            method.settings = json.dumps(method_data.get('settings', {}))
            
            if not existing:
                self.db_session.add(method)
                
            self.db_session.commit()
            
            # Extract and save shipping class rates from settings
            self._save_shipping_class_rates(method.id, method_data.get('settings', {}))
            
        except Exception as e:
            print(f"Error saving shipping method: {e}")
            self.db_session.rollback()
    
    def _save_shipping_class_rates(self, method_id: int, settings: Dict):
        """Extract and save shipping class rates from method settings"""
        try:
            # Clear existing rates for this method
            self.db_session.query(ShippingClassRate).filter_by(method_id=method_id).delete()
            
            # Debug: Print settings to understand the structure
            print(f"Method settings for method {method_id}: {json.dumps(settings, indent=2)}")
            
            # Extract rates from settings - WooCommerce format varies by shipping method type
            for key, setting_data in settings.items():
                if key.startswith('class_cost_'):
                    # Extract shipping class ID from key (e.g., 'class_cost_7' -> 7)
                    try:
                        class_woo_id = int(key.replace('class_cost_', ''))
                    except ValueError:
                        continue
                    
                    # Get the actual cost value - it might be in 'value' field or direct
                    cost_value = '0'
                    if isinstance(setting_data, dict):
                        cost_value = setting_data.get('value', '0')
                    elif isinstance(setting_data, str):
                        cost_value = setting_data
                    else:
                        cost_value = str(setting_data) if setting_data else '0'
                        
                    # Find the shipping class in our database
                    shipping_class = self.db_session.query(ShippingClass).filter_by(
                        site_id=self.site_id,
                        woo_id=class_woo_id
                    ).first()
                    
                    # Create rate entry
                    rate = ShippingClassRate()
                    rate.site_id = self.site_id
                    rate.method_id = method_id
                    rate.shipping_class_id = shipping_class.id if shipping_class else None
                    rate.cost = cost_value
                    
                    # Get calculation type if available
                    calc_key = f'class_calc_{class_woo_id}'
                    calc_data = settings.get(calc_key, {})
                    if isinstance(calc_data, dict):
                        rate.calculation_type = calc_data.get('value', 'flat')
                    else:
                        rate.calculation_type = str(calc_data) if calc_data else 'flat'
                    
                    self.db_session.add(rate)
                    print(f"Added rate for class {class_woo_id}: {cost_value}")
            
            # Handle "no shipping class" rate
            if 'no_class_cost' in settings:
                no_class_data = settings['no_class_cost']
                cost_value = '0'
                if isinstance(no_class_data, dict):
                    cost_value = no_class_data.get('value', '0')
                else:
                    cost_value = str(no_class_data) if no_class_data else '0'
                
                rate = ShippingClassRate()
                rate.site_id = self.site_id
                rate.method_id = method_id
                rate.shipping_class_id = None  # No shipping class
                rate.cost = cost_value
                
                no_calc_data = settings.get('no_class_calc', {})
                if isinstance(no_calc_data, dict):
                    rate.calculation_type = no_calc_data.get('value', 'flat')
                else:
                    rate.calculation_type = str(no_calc_data) if no_calc_data else 'flat'
                
                self.db_session.add(rate)
                print(f"Added no-class rate: {cost_value}")
            
            self.db_session.commit()
            
        except Exception as e:
            print(f"Error saving shipping class rates: {e}")
            self.db_session.rollback()
            
    def save_page_content(self, url: str, content: str, page_type: str = "page"):
        """Save crawled page content to vector store"""
        metadata = {
            "site_id": str(self.site_id) if self.site_id else "",
            "url": url,
            "type": page_type,
            "crawled_at": datetime.utcnow().isoformat()
        }
        
        self.pages_collection.upsert(
            documents=[content],
            metadatas=[metadata],
            ids=[f"site_{self.site_id}_page_{hash(url)}" if self.site_id else f"page_{hash(url)}"]
        )
        
    def create_crawl_log(self) -> CrawlLog:
        """Create a new crawl log entry"""
        if not self.site_id:
            raise ValueError("site_id must be set before creating crawl log")
            
        log = CrawlLog(site_id=self.site_id, status="running")
        self.db_session.add(log)
        self.db_session.commit()
        return log
    
    def update_crawl_log(self, log: CrawlLog, **kwargs):
        """Update crawl log with results"""
        for key, value in kwargs.items():
            setattr(log, key, value)
        self.db_session.commit()
        
    def get_or_create_site(self, site_name: str, site_url: str, consumer_key: str, consumer_secret: str) -> Site:
        """Get existing site by name or create new one"""
        site = self.db_session.query(Site).filter_by(name=site_name).first()
        
        if not site:
            site = Site(
                name=site_name,
                url=site_url,
                consumer_key=consumer_key,
                consumer_secret=consumer_secret
            )
            self.db_session.add(site)
            self.db_session.commit()
        else:
            # Update credentials if they've changed
            site.url = site_url
            site.consumer_key = consumer_key
            site.consumer_secret = consumer_secret
            self.db_session.commit()
            
        return site
    
    def close(self):
        """Close database connections"""
        self.db_session.close()