#!/bin/bash

# Example script to run the crawler

# Check if site name was provided
if [ $# -eq 0 ]; then
    echo "Usage: ./run_crawler.sh <site-name> [sitemap-url]"
    echo "Example: ./run_crawler.sh store1"
    echo "Example: ./run_crawler.sh store1 https://store1.com/product-sitemap.xml"
    exit 1
fi

SITE_NAME=$1
SITEMAP_URL=$2

if [ -z "$SITEMAP_URL" ]; then
    echo "Running crawler for site: $SITE_NAME (default sitemap)"
    python main.py --site-name "$SITE_NAME"
else
    echo "Running crawler for site: $SITE_NAME with custom sitemap: $SITEMAP_URL"
    python main.py --site-name "$SITE_NAME" --sitemap-url "$SITEMAP_URL"
fi

# Legacy single-site usage (if not using multi-site)
# echo "Running crawler with default configuration..."
# python main.py

# Examples of multi-site usage:
# ./run_crawler.sh store1
# ./run_crawler.sh store2 "https://store2.com/products-sitemap.xml"