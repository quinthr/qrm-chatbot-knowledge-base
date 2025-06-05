-- MySQL setup script for MassLoadedVinyl Crawler
-- Run this script to create the database and user

-- Create database
CREATE DATABASE IF NOT EXISTS massloadedvinyl_crawler CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user (update password as needed)
-- CREATE USER 'crawler_user'@'localhost' IDENTIFIED BY 'your_secure_password';

-- Grant privileges
-- GRANT ALL PRIVILEGES ON massloadedvinyl_crawler.* TO 'crawler_user'@'localhost';

-- Flush privileges
-- FLUSH PRIVILEGES;

-- Switch to the database
USE massloadedvinyl_crawler;

-- The tables will be automatically created by SQLAlchemy when the crawler runs