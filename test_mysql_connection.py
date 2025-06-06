#!/usr/bin/env python3
"""
Test MySQL connection with various encoding methods
"""
import os
import sys
from urllib.parse import quote_plus

# Test different password encoding methods
password = os.getenv("MYSQL_PASSWORD", "")
user = os.getenv("MYSQL_USER", "")
host = os.getenv("MYSQL_HOST", "localhost")
database = os.getenv("MYSQL_DATABASE", "")

print("=== MySQL Connection Test ===")
print(f"User: {user}")
print(f"Host: {host}")
print(f"Database: {database}")
print(f"Password length: {len(password)} chars")
print(f"Password contains special chars: {any(c in password for c in '@*~^=')}")
print()

# Try different connection methods
print("=== Testing Connection Methods ===")

# Method 1: Direct pymysql
print("\n1. Testing direct pymysql connection...")
try:
    import pymysql
    conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        charset='utf8mb4'
    )
    print("✓ Direct pymysql connection successful!")
    conn.close()
except Exception as e:
    print(f"✗ Direct pymysql failed: {type(e).__name__}: {e}")

# Method 2: SQLAlchemy with encoded password
print("\n2. Testing SQLAlchemy with URL encoding...")
try:
    from sqlalchemy import create_engine
    encoded_password = quote_plus(password)
    url = f"mysql+pymysql://{user}:{encoded_password}@{host}/{database}?charset=utf8mb4"
    print(f"   Encoded URL: mysql+pymysql://{user}:****@{host}/{database}?charset=utf8mb4")
    
    engine = create_engine(url)
    with engine.connect() as conn:
        result = conn.execute("SELECT 1")
        print("✓ SQLAlchemy connection successful!")
except Exception as e:
    print(f"✗ SQLAlchemy failed: {type(e).__name__}: {e}")

# Method 3: SQLAlchemy with connect_args
print("\n3. Testing SQLAlchemy with connect_args...")
try:
    from sqlalchemy import create_engine
    url = f"mysql+pymysql://{user}:@{host}/{database}"
    engine = create_engine(
        url,
        connect_args={
            'password': password,
            'charset': 'utf8mb4'
        }
    )
    with engine.connect() as conn:
        result = conn.execute("SELECT 1")
        print("✓ SQLAlchemy with connect_args successful!")
except Exception as e:
    print(f"✗ SQLAlchemy with connect_args failed: {type(e).__name__}: {e}")

print("\n=== Recommendations ===")
if any(c in password for c in '@*~^=!#$%&()[]{}'):
    print("Your password contains special characters that may cause issues.")
    print("Consider changing to a password with only letters, numbers, and underscores.")
    print("Example: ChatbotDB2024_Secure")