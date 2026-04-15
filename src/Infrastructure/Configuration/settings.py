"""Configuration management with appsettings.json and environment variables"""
import json
import os
from pathlib import Path
from typing import Any, Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field

class AppSettings(BaseSettings):
    """Application settings that can be overridden by environment variables"""
    
    # Database
    DATABASE_URL: str = Field(default="mysql+pymysql://root:15nR7xCS15EXSvh4I2y9@localhost:3306/conectaceu")
    DATABASE_HOST: str = Field(default="localhost")
    DATABASE_PORT: int = Field(default=3306)
    DATABASE_NAME: str = Field(default="conectaceu")
    DATABASE_USER: str = Field(default="root")
    DATABASE_PASSWORD: str = Field(default="")
    DATABASE_POOL_SIZE: int = Field(default=10)
    DATABASE_MAX_OVERFLOW: int = Field(default=20)
    DATABASE_POOL_RECYCLE: int = Field(default=3600)
    DATABASE_POOL_PRE_PING: bool = Field(default=True)
    DATABASE_ECHO: bool = Field(default=False)
    
    # Security
    SECRET_KEY: str = Field(default="default-secret-key-change-in-production")
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    
    # App configuration
    APP_NAME: str = Field(default="ConectaCEU")
    APP_VERSION: str = Field(default="0.1.0")
    ENVIRONMENT: str = Field(default="Development")
    
    # CORS
    ALLOWED_ORIGINS: list[str] = Field(default=["http://localhost:3000", "http://localhost:8000"])
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = Field(default=10)
    MAX_PAGE_SIZE: int = Field(default=50)
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )

class ConfigurationManager:
    """Manages configuration from JSON files and environment variables"""
    
    _instance: Optional['ConfigurationManager'] = None
    _settings: Optional[AppSettings] = None
    _json_config: dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_configuration()
        return cls._instance
    
    def _load_configuration(self):
        """Load configuration from JSON files based on environment"""
        # Load base configuration
        self._load_json_config("appsettings.json")
        
        # Load environment-specific configuration
        env = os.getenv("ENVIRONMENT", "Development")
        env_config_file = f"appsettings.{env}.json"
        if Path(env_config_file).exists():
            self._load_json_config(env_config_file)
        
        # Load settings from environment variables
        self._settings = AppSettings()
    
    def _load_json_config(self, filepath: str):
        """Load and merge JSON configuration file"""
        try:
            with open(filepath, 'r') as f:
                config = json.load(f)
                self._merge_dicts(self._json_config, config)
        except FileNotFoundError:
            print(f"Warning: Configuration file {filepath} not found")
        except json.JSONDecodeError as e:
            print(f"Error parsing {filepath}: {e}")
    
    def _merge_dicts(self, base: dict, override: dict):
        """Recursively merge dictionaries"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_dicts(base[key], value)
            else:
                base[key] = value
    
    @property
    def settings(self) -> AppSettings:
        """Get application settings"""
        if self._settings is None:
            self._load_configuration()
        return self._settings
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a specific configuration value using dot notation"""
        keys = key.split('.')
        value = self._json_config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value

# Singleton instance for easy import
config = ConfigurationManager()
