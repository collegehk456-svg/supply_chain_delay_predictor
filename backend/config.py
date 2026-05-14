"""
Configuration Management Module
Handles loading and managing application configuration from YAML files and environment variables.
"""

import os
import logging
from typing import Any, Dict, Optional
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)


class Config:
    """Application configuration manager."""

    def __init__(self, config_file: Optional[str] = None, env: str = "default"):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to config YAML file. If None, loads default config.
            env: Environment name (development, production, etc.)
        """
        self.env = env
        self.config_data: Dict[str, Any] = {}
        
        # Load configuration file
        if config_file is None:
            config_file = os.path.join(
                os.path.dirname(__file__), 
                "..", 
                "configs", 
                "default.yaml"
            )
        
        self._load_config(config_file)
        self._load_env_overrides()
    
    def _load_config(self, config_file: str) -> None:
        """Load configuration from YAML file."""
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.config_data = yaml.safe_load(f) or {}
            logger.info(f"Configuration loaded from {config_file}")
        else:
            logger.warning(f"Configuration file not found: {config_file}")
    
    def _load_env_overrides(self) -> None:
        """Override configuration with environment variables."""
        # API Configuration overrides
        if os.getenv("API_HOST"):
            self.config_data.setdefault("api", {})["host"] = os.getenv("API_HOST")
        if os.getenv("API_PORT"):
            self.config_data.setdefault("api", {})["port"] = int(os.getenv("API_PORT"))
        
        # Model Configuration overrides
        if os.getenv("MODEL_PATH"):
            self.config_data.setdefault("model", {})["path"] = os.getenv("MODEL_PATH")
        if os.getenv("MODEL_THRESHOLD"):
            self.config_data.setdefault("model", {})["threshold"] = float(
                os.getenv("MODEL_THRESHOLD")
            )
        
        # Database Configuration overrides
        if os.getenv("DATABASE_URL"):
            self.config_data.setdefault("database", {})["url"] = os.getenv("DATABASE_URL")
        
        # MLflow Configuration overrides
        if os.getenv("MLFLOW_TRACKING_URI"):
            self.config_data.setdefault("mlflow", {})["tracking_uri"] = os.getenv(
                "MLFLOW_TRACKING_URI"
            )
        
        # Logging Configuration overrides
        if os.getenv("LOG_LEVEL"):
            self.config_data.setdefault("logging", {})["level"] = os.getenv("LOG_LEVEL")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key using dot notation.
        
        Args:
            key: Configuration key (e.g., 'api.port', 'model.path')
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def get_dict(self, key: str) -> Dict[str, Any]:
        """Get configuration section as dictionary."""
        return self.get(key, {})
    
    def __getitem__(self, key: str) -> Any:
        """Support dictionary-style access."""
        return self.get(key)


# Global config instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


def reload_config(config_file: Optional[str] = None) -> Config:
    """Reload configuration."""
    global _config_instance
    _config_instance = Config(config_file=config_file)
    return _config_instance
