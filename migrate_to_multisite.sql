-- Migration script to add multi-site support to existing crawler database
-- Backup your database before running this script!

-- 1. Create sites table
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

-- 2. Insert a default site for existing data
INSERT INTO sites (name, url, consumer_key, consumer_secret) 
VALUES ('default', 'https://your-existing-site.com', 'update_with_actual_key', 'update_with_actual_secret');

-- Get the ID of the default site
SET @default_site_id = LAST_INSERT_ID();

-- 3. Add site_id columns to existing tables
ALTER TABLE products 
ADD COLUMN site_id INTEGER AFTER id,
ADD CONSTRAINT fk_products_site FOREIGN KEY (site_id) REFERENCES sites(id);

ALTER TABLE product_variations
ADD COLUMN site_id INTEGER AFTER id,
ADD CONSTRAINT fk_variations_site FOREIGN KEY (site_id) REFERENCES sites(id);

ALTER TABLE categories
ADD COLUMN site_id INTEGER AFTER id,
ADD CONSTRAINT fk_categories_site FOREIGN KEY (site_id) REFERENCES sites(id);

ALTER TABLE shipping_zones
ADD COLUMN site_id INTEGER AFTER id,
ADD CONSTRAINT fk_zones_site FOREIGN KEY (site_id) REFERENCES sites(id);

ALTER TABLE shipping_methods
ADD COLUMN site_id INTEGER AFTER id,
ADD CONSTRAINT fk_methods_site FOREIGN KEY (site_id) REFERENCES sites(id);

ALTER TABLE shipping_classes
ADD COLUMN site_id INTEGER AFTER id,
ADD CONSTRAINT fk_classes_site FOREIGN KEY (site_id) REFERENCES sites(id);

ALTER TABLE crawl_logs
ADD COLUMN site_id INTEGER AFTER id,
ADD CONSTRAINT fk_logs_site FOREIGN KEY (site_id) REFERENCES sites(id);

-- 4. Update existing records with default site_id
UPDATE products SET site_id = @default_site_id WHERE site_id IS NULL;
UPDATE product_variations SET site_id = @default_site_id WHERE site_id IS NULL;
UPDATE categories SET site_id = @default_site_id WHERE site_id IS NULL;
UPDATE shipping_zones SET site_id = @default_site_id WHERE site_id IS NULL;
UPDATE shipping_methods SET site_id = @default_site_id WHERE site_id IS NULL;
UPDATE shipping_classes SET site_id = @default_site_id WHERE site_id IS NULL;
UPDATE crawl_logs SET site_id = @default_site_id WHERE site_id IS NULL;

-- 5. Make site_id NOT NULL after populating
ALTER TABLE products MODIFY site_id INTEGER NOT NULL;
ALTER TABLE product_variations MODIFY site_id INTEGER NOT NULL;
ALTER TABLE categories MODIFY site_id INTEGER NOT NULL;
ALTER TABLE shipping_zones MODIFY site_id INTEGER NOT NULL;
ALTER TABLE shipping_methods MODIFY site_id INTEGER NOT NULL;
ALTER TABLE shipping_classes MODIFY site_id INTEGER NOT NULL;
ALTER TABLE crawl_logs MODIFY site_id INTEGER NOT NULL;

-- 6. Drop old unique constraints and add new ones with site_id
ALTER TABLE products 
DROP INDEX woo_id,
ADD UNIQUE KEY unique_site_product (site_id, woo_id);

ALTER TABLE product_variations
DROP INDEX woo_id,
ADD UNIQUE KEY unique_site_variation (site_id, woo_id);

ALTER TABLE categories
DROP INDEX woo_id,
ADD UNIQUE KEY unique_site_category (site_id, woo_id);

ALTER TABLE shipping_zones
DROP INDEX woo_id,
ADD UNIQUE KEY unique_site_zone (site_id, woo_id);

ALTER TABLE shipping_classes
DROP INDEX woo_id,
ADD UNIQUE KEY unique_site_class (site_id, woo_id);

-- Remove unique constraint from slug fields as they should be unique per site, not globally
ALTER TABLE products DROP INDEX slug;
ALTER TABLE categories DROP INDEX slug;
ALTER TABLE shipping_classes DROP INDEX slug;

-- 7. Update the sites table with your actual WooCommerce credentials
-- UPDATE sites SET url = 'https://your-actual-site.com', consumer_key = 'your_actual_key', consumer_secret = 'your_actual_secret' WHERE name = 'default';