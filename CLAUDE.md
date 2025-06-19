# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Commands

### Running the Crawler
```bash
# Basic crawling for a specific site
python main.py --site-name store1

# With custom sitemap URL
python main.py --site-name store1 --sitemap-url "https://site.com/product-sitemap.xml"

# Using the bash wrapper
./run_crawler.sh store1
./run_crawler.sh store1 "https://custom-sitemap.xml"
```

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Test basic functionality
python test_basic.py

# Debug configuration
python debug_config.py
```

### Database Setup
```bash
# For MySQL (production)
mysql -u root -p < setup_mysql.sql

# For multi-site migration
mysql -u root -p chatbot_knowledge_base < migrate_to_multisite.sql
```

## Architecture Overview

This is a WooCommerce data crawler that extracts product information and stores it in both SQL databases and ChromaDB for semantic search capabilities. The system supports multiple WooCommerce stores through a multi-site configuration.

### Key Components

1. **Multi-Site Configuration**: Each site is configured with environment variables (SITE_STORE1_URL, SITE_STORE1_CONSUMER_KEY, etc.) and identified by a site_name parameter.

2. **Data Flow**:
   - `main.py` orchestrates the crawling process
   - `src/sitemap_parser.py` discovers products via Yoast SEO sitemaps
   - `src/woocommerce_client.py` fetches data from WooCommerce REST API
   - `src/storage.py` persists data to both SQL and ChromaDB
   - `src/models.py` defines SQLAlchemy ORM models for all database tables

3. **Storage Strategy**:
   - **SQL Database**: Stores structured data (products, categories, shipping info)
   - **ChromaDB**: Stores vector embeddings for semantic search
   - Each site has its own ChromaDB collection for data isolation

4. **Configuration Management**: Uses Pydantic models in `src/config.py` for type-safe configuration with validation.

## Important Implementation Details

- The crawler uses WooCommerce REST API v3 for data extraction (not web scraping)
- Supports both MySQL (production) and SQLite (development) databases
- OpenAI embeddings are generated for products to enable semantic search
- Each crawl session is logged with statistics in the database
- The system is designed to run as scheduled cron jobs for regular updates
- All multi-site data is isolated by site_id in the database

## Recent Updates (2025-01-17)

### Database Schema Changes
- **shipping_zones.locations**: Added TEXT column storing JSON array of location restrictions (countries, states, postcodes)
- **shipping_classes.name**: Changed from VARCHAR(255) to TEXT to prevent name truncation
- **shipping_class_rates**: New table linking shipping methods to class-specific pricing
- **product_variations**: Fixed crawling logic to properly store variation prices and attributes

### New Features
1. **Shipping Zone Locations**: Captures postcodes/regions for accurate shipping zone targeting
2. **Product Variations**: Properly stores and indexes all product variation data including prices
3. **Shipping Class Rates**: Links shipping methods to shipping class costs for accurate pricing
4. **Enhanced Data Quality**: Improved field sizes and data extraction accuracy

### Database Queries for New Features
```sql
-- Get shipping zones with their location restrictions
SELECT sz.name, sz.locations FROM shipping_zones sz WHERE sz.site_id = ?;

-- Get product variations with pricing
SELECT p.name, pv.sku, pv.price, pv.attributes 
FROM products p 
JOIN product_variations pv ON p.id = pv.product_id 
WHERE p.site_id = ?;

-- Get shipping costs by class and method
SELECT sm.title as method, sc.name as class, scr.cost, scr.calculation_type
FROM shipping_class_rates scr
JOIN shipping_methods sm ON scr.method_id = sm.id
JOIN shipping_classes sc ON scr.shipping_class_id = sc.id
WHERE scr.site_id = ?;
```