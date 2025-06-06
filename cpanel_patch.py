#!/usr/bin/env python3
"""
Quick patch for cPanel deployment to handle missing .env file and special characters in passwords
Run this on your cPanel server after uploading files
"""
import os
import shutil

print("Applying cPanel patches...")

# Backup and replace config.py
src_dir = os.path.join(os.path.dirname(__file__), 'src')
config_file = os.path.join(src_dir, 'config.py')
config_backup = os.path.join(src_dir, 'config_original.py')
config_cpanel_fixed = os.path.join(src_dir, 'config_cpanel_fixed.py')
config_cpanel = os.path.join(src_dir, 'config_cpanel.py')

# Use the fixed version if available, otherwise use regular cpanel version
if os.path.exists(config_cpanel_fixed):
    config_source = config_cpanel_fixed
    print("Using config_cpanel_fixed.py (with password encoding fix)")
elif os.path.exists(config_cpanel):
    config_source = config_cpanel
    print("Using config_cpanel.py")
else:
    print("✗ No cPanel config file found!")
    exit(1)

# Backup original
if not os.path.exists(config_backup):
    shutil.copy2(config_file, config_backup)
    print(f"✓ Backed up original config.py to config_original.py")

# Replace with cPanel version
shutil.copy2(config_source, config_file)
print(f"✓ Replaced config.py with cPanel-compatible version")

print("\nPatch complete. You can now run:")
print("  python main.py --site-name store1")