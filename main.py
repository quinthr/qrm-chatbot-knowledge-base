#!/usr/bin/env python3
import sys
import time
import argparse
from datetime import datetime
import traceback

from src.config import config
from src.sitemap_parser import SitemapParser
from src.woocommerce_client import WooCommerceClient
from src.storage import DataStorage
from src import models


def main():
    """Main crawler function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="WooCommerce Product Crawler")
    parser.add_argument(
        "--sitemap-url",
        type=str,
        help="Custom sitemap URL to crawl (defaults to /sitemap.xml on the WooCommerce URL)"
    )
    parser.add_argument(
        "--site-name",
        type=str,
        help="Name of the site to crawl (as configured in .env file)"
    )
    args = parser.parse_args()
    
    print("Starting WooCommerce Crawler...")
    
    try:
        # Get site configuration
        site_config = config.get_site_config(args.site_name)
        print(f"Crawling site: {site_config.name} ({site_config.url})")
    except ValueError as e:
        print(f"Error: {e}")
        print("\nAvailable sites:")
        for site_name in config.sites:
            print(f"  - {site_name}")
        if config.woocommerce.url:
            print("  - (default/legacy configuration)")
        sys.exit(1)
    
    # Initialize storage and get/create site in database
    storage = DataStorage()
    site = storage.get_or_create_site(
        site_name=site_config.name,
        site_url=str(site_config.url),
        consumer_key=site_config.consumer_key,
        consumer_secret=site_config.consumer_secret
    )
    
    # Get site_id before closing session
    site_id = site.id
    
    # Re-initialize storage with site_id
    storage.close()
    storage = DataStorage(site_id=site_id)
    
    # Initialize components with site-specific configuration
    woo_client = WooCommerceClient(site_config)
    sitemap_parser = SitemapParser(str(site_config.url))
    
    # Create crawl log
    crawl_log = storage.create_crawl_log()
    
    try:
        # 1. Parse sitemap
        print("\n1. Parsing sitemap...")
        if args.sitemap_url:
            print(f"   Using custom sitemap URL: {args.sitemap_url}")
        else:
            print(f"   Using default sitemap URL: {site_config.url}/sitemap.xml")
        
        sitemap_urls = sitemap_parser.parse_sitemap(args.sitemap_url)
        categorized_urls = sitemap_parser.categorize_urls(sitemap_urls)
        
        print(f"Found {len(sitemap_urls)} URLs in sitemap:")
        for category, urls in categorized_urls.items():
            print(f"  - {category}: {len(urls)} URLs")
        
        # 2. Fetch WooCommerce data via API
        print("\n2. Fetching WooCommerce data via API...")
        
        # Categories
        print("  - Fetching categories...")
        categories = woo_client.get_all_categories()
        saved_categories = storage.save_categories(categories)
        print(f"    Saved {saved_categories} categories")
        
        # Products
        print("  - Fetching products...")
        products = woo_client.get_all_products()
        saved_products = storage.save_products(products)
        print(f"    Saved {saved_products} products")
        
        # Product variations
        print("  - Fetching product variations...")
        variation_count = 0
        for product in products:
            if product.get('type') == 'variable':
                # Get the product from database to get its ID
                db_product = storage.db_session.query(models.Product).filter_by(
                    site_id=site_id,
                    woo_id=product['id']
                ).first()
                
                if db_product:
                    variations = woo_client.get_product_variations(product['id'])
                    saved_variations = storage.save_product_variations(db_product.id, variations)
                    variation_count += saved_variations
                    time.sleep(config.crawler.delay_seconds)
                    
        print(f"    Saved {variation_count} product variations")
        
        # Shipping data
        print("  - Fetching shipping data...")
        shipping_zones = woo_client.get_shipping_zones()
        shipping_classes = woo_client.get_shipping_classes()
        storage.save_shipping_data(shipping_zones, shipping_classes)
        print(f"    Saved {len(shipping_zones)} shipping zones")
        print(f"    Saved {len(shipping_classes)} shipping classes")
        
        # 3. Crawl additional pages (optional)
        # This could be used to crawl static pages for additional context
        # For now, we'll skip this as WooCommerce API provides most data
        
        # Update crawl log
        storage.update_crawl_log(
            crawl_log,
            completed_at=datetime.utcnow(),
            status="completed",
            products_crawled=saved_products,
            categories_crawled=saved_categories
        )
        
        print("\n✅ Crawl completed successfully!")
        print(f"Site: {site_config.name}")
        print(f"Total products: {saved_products}")
        print(f"Total product variations: {variation_count}")
        print(f"Total categories: {saved_categories}")
        print(f"Total shipping zones: {len(shipping_zones)}")
        
    except Exception as e:
        print(f"\n❌ Error during crawl: {e}")
        traceback.print_exc()
        
        # Update crawl log with error
        storage.update_crawl_log(
            crawl_log,
            completed_at=datetime.utcnow(),
            status="failed",
            errors=str(e)
        )
        
    finally:
        storage.close()


if __name__ == "__main__":
    main()