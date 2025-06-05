#!/usr/bin/env python3
import os
from dotenv import load_dotenv

load_dotenv()

print("Environment Variables:")
print(f"MYSQL_HOST: '{os.getenv('MYSQL_HOST', 'localhost')}'")
print(f"MYSQL_USER: '{os.getenv('MYSQL_USER', 'root')}'")
print(f"MYSQL_DATABASE: '{os.getenv('MYSQL_DATABASE', 'massloadedvinyl_crawler')}'")

from src.config import config

print(f"\nConfig Values:")
print(f"mysql_user: '{config.database.mysql_user}'")
print(f"mysql_database: '{config.database.mysql_database}'")
print(f"is_mysql: {config.database.is_mysql}")
print(f"database_url: {config.database.url}")