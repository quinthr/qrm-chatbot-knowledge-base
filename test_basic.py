#!/usr/bin/env python3
"""
Basic test to verify the crawler setup works
Run: python3 test_basic.py
"""

print("Testing crawler basic functionality...")

# Test 1: Can we import basic modules?
try:
    import os
    import sys
    import json
    from urllib.parse import urljoin
    print("✅ Basic Python modules imported successfully")
except ImportError as e:
    print(f"❌ Failed to import basic modules: {e}")
    sys.exit(1)

# Test 2: Check if .env file exists
env_file = ".env"
if os.path.exists(env_file):
    print("✅ .env file found")
    with open(env_file, 'r') as f:
        content = f.read()
        if "SITE_STORE1_URL" in content:
            print("✅ Site configuration found in .env")
        else:
            print("❌ Site configuration not found in .env")
else:
    print("❌ .env file not found")

# Test 3: Check directory structure
dirs_to_check = ["src", "data", "logs"]
for dir_name in dirs_to_check:
    if os.path.exists(dir_name):
        print(f"✅ Directory '{dir_name}' exists")
    else:
        print(f"⚠️  Directory '{dir_name}' missing - will be created when needed")

# Test 4: Check Python files
files_to_check = [
    "src/config.py", 
    "src/sitemap_parser.py", 
    "src/woocommerce_client.py",
    "src/storage.py",
    "src/models.py"
]

for file_path in files_to_check:
    if os.path.exists(file_path):
        print(f"✅ File '{file_path}' exists")
    else:
        print(f"❌ File '{file_path}' missing")

print("\n🎯 Next steps:")
print("1. Install Python dependencies:")
print("   sudo apt install python3-pip")
print("   pip3 install -r requirements.txt")
print("")
print("2. Test the full crawler:")
print("   python3 main.py --site-name store1")
print("")
print("3. The crawler will use SQLite locally (no MySQL needed for testing)")