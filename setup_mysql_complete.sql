-- Complete MySQL setup script for QRM Chatbot Knowledge Base
-- This creates all necessary tables for the multi-site crawler

-- Create sites table
CREATE TABLE IF NOT EXISTS sites (
    id INTEGER NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    url VARCHAR(500) NOT NULL,
    consumer_key VARCHAR(255) NOT NULL,
    consumer_secret VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id INTEGER NOT NULL AUTO_INCREMENT,
    site_id INTEGER NOT NULL,
    woo_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    permalink VARCHAR(500),
    type VARCHAR(50),
    status VARCHAR(50),
    description TEXT,
    short_description TEXT,
    sku VARCHAR(100),
    price VARCHAR(50),
    regular_price VARCHAR(50),
    sale_price VARCHAR(50),
    on_sale BOOLEAN DEFAULT FALSE,
    stock_status VARCHAR(50),
    stock_quantity INTEGER,
    weight VARCHAR(50),
    dimensions_length VARCHAR(50),
    dimensions_width VARCHAR(50),
    dimensions_height VARCHAR(50),
    shipping_class VARCHAR(100),
    shipping_class_id INTEGER,
    categories TEXT,
    tags TEXT,
    images TEXT,
    attributes TEXT,
    variations TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY unique_site_product (site_id, woo_id),
    CONSTRAINT fk_products_site FOREIGN KEY (site_id) REFERENCES sites(id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create product_variations table
CREATE TABLE IF NOT EXISTS product_variations (
    id INTEGER NOT NULL AUTO_INCREMENT,
    site_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    woo_id INTEGER NOT NULL,
    sku VARCHAR(100),
    price VARCHAR(50),
    regular_price VARCHAR(50),
    sale_price VARCHAR(50),
    on_sale BOOLEAN DEFAULT FALSE,
    stock_status VARCHAR(50),
    stock_quantity INTEGER,
    weight VARCHAR(50),
    dimensions_length VARCHAR(50),
    dimensions_width VARCHAR(50),
    dimensions_height VARCHAR(50),
    attributes TEXT,
    image VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY unique_site_variation (site_id, woo_id),
    CONSTRAINT fk_variations_site FOREIGN KEY (site_id) REFERENCES sites(id),
    CONSTRAINT fk_variations_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create categories table
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER NOT NULL AUTO_INCREMENT,
    site_id INTEGER NOT NULL,
    woo_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    parent INTEGER DEFAULT 0,
    description TEXT,
    count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY unique_site_category (site_id, woo_id),
    CONSTRAINT fk_categories_site FOREIGN KEY (site_id) REFERENCES sites(id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create shipping_zones table
CREATE TABLE IF NOT EXISTS shipping_zones (
    id INTEGER NOT NULL AUTO_INCREMENT,
    site_id INTEGER NOT NULL,
    woo_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    order_zone INTEGER DEFAULT 0,
    locations TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY unique_site_zone (site_id, woo_id),
    CONSTRAINT fk_zones_site FOREIGN KEY (site_id) REFERENCES sites(id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create shipping_methods table
CREATE TABLE IF NOT EXISTS shipping_methods (
    id INTEGER NOT NULL AUTO_INCREMENT,
    site_id INTEGER NOT NULL,
    zone_id INTEGER NOT NULL,
    instance_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    order_method INTEGER DEFAULT 0,
    enabled BOOLEAN DEFAULT TRUE,
    method_id VARCHAR(100),
    method_title VARCHAR(255),
    method_description TEXT,
    settings TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_methods_site FOREIGN KEY (site_id) REFERENCES sites(id),
    CONSTRAINT fk_methods_zone FOREIGN KEY (zone_id) REFERENCES shipping_zones(id) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create shipping_classes table  
CREATE TABLE IF NOT EXISTS shipping_classes (
    id INTEGER NOT NULL AUTO_INCREMENT,
    site_id INTEGER NOT NULL,
    woo_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    slug VARCHAR(255) NOT NULL,
    description TEXT,
    count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY unique_site_class (site_id, woo_id),
    CONSTRAINT fk_classes_site FOREIGN KEY (site_id) REFERENCES sites(id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create shipping_class_rates table
CREATE TABLE IF NOT EXISTS shipping_class_rates (
    id INTEGER NOT NULL AUTO_INCREMENT,
    site_id INTEGER NOT NULL,
    method_id INTEGER NOT NULL,
    shipping_class_id INTEGER,
    cost VARCHAR(50),
    calculation_type VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_rates_site FOREIGN KEY (site_id) REFERENCES sites(id),
    CONSTRAINT fk_rates_method FOREIGN KEY (method_id) REFERENCES shipping_methods(id) ON DELETE CASCADE,
    CONSTRAINT fk_rates_class FOREIGN KEY (shipping_class_id) REFERENCES shipping_classes(id) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create crawl_logs table
CREATE TABLE IF NOT EXISTS crawl_logs (
    id INTEGER NOT NULL AUTO_INCREMENT,
    site_id INTEGER NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    status VARCHAR(50),
    products_crawled INTEGER DEFAULT 0,
    variations_crawled INTEGER DEFAULT 0,
    categories_crawled INTEGER DEFAULT 0,
    shipping_zones_crawled INTEGER DEFAULT 0,
    shipping_methods_crawled INTEGER DEFAULT 0,
    shipping_classes_crawled INTEGER DEFAULT 0,
    errors TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_logs_site FOREIGN KEY (site_id) REFERENCES sites(id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create indexes for better performance
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_status ON products(status);
CREATE INDEX idx_products_created ON products(created_at);
CREATE INDEX idx_variations_sku ON product_variations(sku);
CREATE INDEX idx_categories_parent ON categories(parent);
CREATE INDEX idx_crawl_logs_start ON crawl_logs(start_time);

-- Insert store1 site configuration (will be populated from environment variables)
INSERT INTO sites (name, url, consumer_key, consumer_secret) 
VALUES ('store1', 'https://placeholder.com', 'placeholder_key', 'placeholder_secret')
ON DUPLICATE KEY UPDATE name=name;