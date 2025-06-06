#!/usr/bin/env python3
"""
Quick patch for cPanel deployment to handle missing .env file
Run this on your cPanel server after uploading files
"""
import os
import shutil

print("Applying cPanel patches...")

# Backup and replace config.py
src_dir = os.path.join(os.path.dirname(__file__), 'src')
config_file = os.path.join(src_dir, 'config.py')
config_backup = os.path.join(src_dir, 'config_original.py')
config_cpanel = os.path.join(src_dir, 'config_cpanel.py')

if os.path.exists(config_cpanel):
    # Backup original
    if not os.path.exists(config_backup):
        shutil.copy2(config_file, config_backup)
        print(f"✓ Backed up original config.py to config_original.py")
    
    # Replace with cPanel version
    shutil.copy2(config_cpanel, config_file)
    print(f"✓ Replaced config.py with cPanel-compatible version")
else:
    print("✗ config_cpanel.py not found!")

print("\nPatch complete. You can now run:")
print("  python main.py --site-name store1")