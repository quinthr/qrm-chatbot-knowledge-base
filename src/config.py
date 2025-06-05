import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel, HttpUrl
from typing import Dict, Optional

load_dotenv()


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
        """Check if using MySQL"""
        return bool(
            self.mysql_user and 
            self.mysql_database and 
            self.mysql_user.strip() and 
            self.mysql_database.strip() and
            self.mysql_user != "your_mysql_user"
        )
    
    chroma_persist_directory: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/chroma")


class Config:
    def __init__(self):
        # Legacy single-site configuration (for backward compatibility)
        self.woocommerce = WooCommerceConfig(
            url=os.getenv("WOOCOMMERCE_URL", None),
            consumer_key=os.getenv("WOOCOMMERCE_CONSUMER_KEY", ""),
            consumer_secret=os.getenv("WOOCOMMERCE_CONSUMER_SECRET", "")
        )
        
        self.crawler = CrawlerConfig()
        self.database = DatabaseConfig()
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        
        # Multi-site configuration
        self.sites: Dict[str, SiteConfig] = {}
        # Load sites from environment variables
        # Format: SITE_<NAME>_URL, SITE_<NAME>_CONSUMER_KEY, SITE_<NAME>_CONSUMER_SECRET
        site_prefixes = set()
        for key in os.environ:
            if key.startswith("SITE_") and "_URL" in key:
                prefix = key.split("_URL")[0]
                site_prefixes.add(prefix)
        
        for prefix in site_prefixes:
            site_name = prefix.replace("SITE_", "").lower()
            url = os.getenv(f"{prefix}_URL")
            consumer_key = os.getenv(f"{prefix}_CONSUMER_KEY")
            consumer_secret = os.getenv(f"{prefix}_CONSUMER_SECRET")
            
            if url and consumer_key and consumer_secret:
                self.sites[site_name] = SiteConfig(
                    name=site_name,
                    url=url,
                    consumer_key=consumer_key,
                    consumer_secret=consumer_secret
                )
    
    def get_site_config(self, site_name: Optional[str] = None) -> SiteConfig:
        """Get configuration for a specific site or default site"""
        if site_name and site_name in self.sites:
            return self.sites[site_name]
        elif not site_name and self.woocommerce.url:
            # Return legacy config as SiteConfig for backward compatibility
            return SiteConfig(
                name="default",
                url=str(self.woocommerce.url),
                consumer_key=self.woocommerce.consumer_key,
                consumer_secret=self.woocommerce.consumer_secret
            )
        else:
            raise ValueError(f"Site '{site_name}' not found in configuration")


config = Config()