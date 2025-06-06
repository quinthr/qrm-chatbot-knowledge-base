import os
import json
from pydantic import BaseModel, HttpUrl
from typing import Dict, Optional

# Try to load dotenv, but don't fail if .env doesn't exist
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # If dotenv fails, continue with system environment variables
    pass


class WooCommerceConfig(BaseModel):
    url: Optional[HttpUrl] = None
    consumer_key: str = ""
    consumer_secret: str = ""


class SiteConfig(BaseModel):
    """Configuration for a single WooCommerce site"""
    name: str
    url: HttpUrl
    consumer_key: str
    consumer_secret: str


class CrawlerConfig(BaseModel):
    user_agent: str = os.getenv("CRAWLER_USER_AGENT", "MassLoadedVinyl-Bot/1.0")
    delay_seconds: int = int(os.getenv("CRAWLER_DELAY_SECONDS", "1"))
    timeout_seconds: int = int(os.getenv("CRAWLER_TIMEOUT_SECONDS", "30"))


class DatabaseConfig(BaseModel):
    # MySQL connection parameters
    mysql_host: str = os.getenv("MYSQL_HOST", "")
    mysql_port: int = int(os.getenv("MYSQL_PORT", "3306"))
    mysql_user: str = os.getenv("MYSQL_USER", "")
    mysql_password: str = os.getenv("MYSQL_PASSWORD", "")
    mysql_database: str = os.getenv("MYSQL_DATABASE", "")
    
    @property
    def url(self) -> str:
        """Return database URL - MySQL if configured, otherwise SQLite"""
        if (self.mysql_user and self.mysql_database and 
            self.mysql_user.strip() and self.mysql_database.strip() and
            self.mysql_user != "your_mysql_user"):
            return f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}?charset=utf8mb4"
        else:
            # Fallback to SQLite for local development
            return "sqlite:///data/products.db"
    
    @property
    def is_mysql(self) -> bool:
        """Check if MySQL is configured"""
        return bool(self.mysql_user and self.mysql_database and 
                   self.mysql_user.strip() and self.mysql_database.strip() and
                   self.mysql_user != "your_mysql_user")


class Config(BaseModel):
    # Load sites from environment with format SITE_[NAME]_URL, etc.
    sites: Dict[str, SiteConfig] = {}
    database: DatabaseConfig = DatabaseConfig()
    crawler: CrawlerConfig = CrawlerConfig()
    
    # OpenAI settings
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # ChromaDB settings
    chroma_persist_directory: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/chroma")
    
    def __init__(self, **data):
        super().__init__(**data)
        # Load sites from environment
        self._load_sites_from_env()
    
    def _load_sites_from_env(self):
        """Load site configurations from environment variables"""
        site_names = set()
        
        # Find all site names from environment variables
        for key in os.environ:
            if key.startswith("SITE_") and "_URL" in key:
                # Extract site name from SITE_[NAME]_URL pattern
                parts = key.split("_")
                if len(parts) >= 3:
                    site_name = parts[1].lower()
                    site_names.add(site_name)
        
        # Load configuration for each site
        for site_name in site_names:
            prefix = f"SITE_{site_name.upper()}"
            
            url = os.getenv(f"{prefix}_URL")
            consumer_key = os.getenv(f"{prefix}_CONSUMER_KEY", "")
            consumer_secret = os.getenv(f"{prefix}_CONSUMER_SECRET", "")
            
            if url and consumer_key and consumer_secret:
                self.sites[site_name] = SiteConfig(
                    name=site_name,
                    url=url,
                    consumer_key=consumer_key,
                    consumer_secret=consumer_secret
                )
    
    def get_site(self, site_name: str) -> Optional[SiteConfig]:
        """Get configuration for a specific site"""
        return self.sites.get(site_name)


# Global config instance
config = Config()