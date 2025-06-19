#!/usr/bin/env python3
"""
Fix for MySQL charset encoding issue with pymysql 1.0.3
"""
import os
import sys

def fix_mysql_connection():
    """Update models.py to handle charset more robustly"""
    
    models_path = "src/models.py"
    
    # Read the current content
    with open(models_path, 'r') as f:
        content = f.read()
    
    # Replace the get_database_session function with a more robust version
    new_function = '''
def get_database_session(database_url: str):
    """Create database engine and return session"""
    # Add MySQL-specific connection options
    if database_url.startswith("mysql"):
        # Parse and rebuild URL with proper charset handling
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
        
        parsed = urlparse(database_url)
        query_params = parse_qs(parsed.query)
        
        # Ensure charset is set properly
        query_params['charset'] = ['utf8mb4']
        
        # Rebuild the URL
        new_query = urlencode(query_params, doseq=True)
        database_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
        
        # Create engine with additional MySQL-specific options
        engine = create_engine(
            database_url,
            pool_pre_ping=True,  # Verify connections before using them
            pool_recycle=3600,   # Recycle connections after 1 hour
            connect_args={
                'charset': 'utf8mb4',
                'use_unicode': True
            }
        )
    else:
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
    
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()'''
    
    # Find and replace the function
    import re
    pattern = r'def get_database_session\(database_url: str\):.*?return Session\(\)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        content = content[:match.start()] + new_function + content[match.end():]
        
        # Write the updated content
        with open(models_path, 'w') as f:
            f.write(content)
        
        print(f"Updated {models_path} with improved charset handling")
        return True
    else:
        print(f"Could not find get_database_session function in {models_path}")
        return False

def update_config_files():
    """Update config files to use simpler charset specification"""
    config_files = ['src/config.py', 'src/config_cpanel.py']
    
    for config_file in config_files:
        if not os.path.exists(config_file):
            continue
            
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Replace the MySQL URL construction to use simpler charset
        old_line = 'return f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}?charset=utf8mb4"'
        new_line = 'return f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"'
        
        if old_line in content:
            content = content.replace(old_line, new_line)
            with open(config_file, 'w') as f:
                f.write(content)
            print(f"Updated {config_file} to remove charset from URL")

if __name__ == "__main__":
    print("Fixing MySQL charset encoding issue...")
    
    # First update config files
    update_config_files()
    
    # Then update models.py
    if fix_mysql_connection():
        print("\nFix applied successfully!")
        print("The connection will now handle charset encoding properly.")
    else:
        print("\nFailed to apply fix.")
        sys.exit(1)