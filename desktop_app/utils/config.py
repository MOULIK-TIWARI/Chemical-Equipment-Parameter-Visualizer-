"""
Configuration management for Chemical Equipment Analytics Desktop Application.

This module provides centralized configuration management, loading settings from
a config.ini file and providing default values.

Requirements: 1.2
"""

import configparser
import os
from pathlib import Path
from typing import Any, Optional


class Config:
    """
    Configuration manager for the desktop application.
    
    Loads settings from config.ini file and provides access to configuration
    values with appropriate defaults.
    
    Attributes:
        config_file (Path): Path to the configuration file
        _config (ConfigParser): Internal configuration parser
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to config file (default: config.ini in app directory)
        """
        if config_file is None:
            # Default to config.ini in the desktop_app directory
            app_dir = Path(__file__).parent.parent
            config_file = app_dir / 'config.ini'
        
        self.config_file = Path(config_file)
        self._config = configparser.ConfigParser()
        
        # Load configuration
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file, creating default if not exists."""
        if self.config_file.exists():
            self._config.read(self.config_file)
        else:
            # Create default configuration
            self._create_default_config()
    
    def _create_default_config(self):
        """Create a default configuration file."""
        self._config['API'] = {
            'base_url': 'http://localhost:8000/api',
            'timeout': '30'
        }
        
        self._config['Application'] = {
            'app_name': 'Chemical Equipment Analytics',
            'window_width': '1200',
            'window_height': '800',
            'max_file_size_mb': '10'
        }
        
        self._config['Data'] = {
            'page_size': '50',
            'default_chart_type': 'bar'
        }
        
        self._config['Paths'] = {
            'temp_dir': 'temp',
            'reports_dir': 'reports'
        }
        
        # Save the default configuration
        self.save()
    
    def save(self):
        """Save current configuration to file."""
        try:
            # Ensure parent directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                self._config.write(f)
        except Exception as e:
            print(f"Warning: Could not save configuration: {e}")
    
    def get(self, section: str, key: str, fallback: Any = None) -> str:
        """
        Get a configuration value.
        
        Args:
            section: Configuration section name
            key: Configuration key name
            fallback: Default value if key not found
            
        Returns:
            Configuration value as string
        """
        return self._config.get(section, key, fallback=fallback)
    
    def get_int(self, section: str, key: str, fallback: int = 0) -> int:
        """
        Get a configuration value as integer.
        
        Args:
            section: Configuration section name
            key: Configuration key name
            fallback: Default value if key not found
            
        Returns:
            Configuration value as integer
        """
        try:
            return self._config.getint(section, key, fallback=fallback)
        except ValueError:
            return fallback
    
    def get_float(self, section: str, key: str, fallback: float = 0.0) -> float:
        """
        Get a configuration value as float.
        
        Args:
            section: Configuration section name
            key: Configuration key name
            fallback: Default value if key not found
            
        Returns:
            Configuration value as float
        """
        try:
            return self._config.getfloat(section, key, fallback=fallback)
        except ValueError:
            return fallback
    
    def get_bool(self, section: str, key: str, fallback: bool = False) -> bool:
        """
        Get a configuration value as boolean.
        
        Args:
            section: Configuration section name
            key: Configuration key name
            fallback: Default value if key not found
            
        Returns:
            Configuration value as boolean
        """
        try:
            return self._config.getboolean(section, key, fallback=fallback)
        except ValueError:
            return fallback
    
    def set(self, section: str, key: str, value: Any):
        """
        Set a configuration value.
        
        Args:
            section: Configuration section name
            key: Configuration key name
            value: Value to set
        """
        if not self._config.has_section(section):
            self._config.add_section(section)
        
        self._config.set(section, key, str(value))
    
    # Convenience properties for commonly used settings
    
    @property
    def api_base_url(self) -> str:
        """Get the API base URL."""
        return self.get('API', 'base_url', 'http://localhost:8000/api')
    
    @api_base_url.setter
    def api_base_url(self, value: str):
        """Set the API base URL."""
        self.set('API', 'base_url', value)
    
    @property
    def api_timeout(self) -> int:
        """Get the API request timeout in seconds."""
        return self.get_int('API', 'timeout', 30)
    
    @api_timeout.setter
    def api_timeout(self, value: int):
        """Set the API request timeout in seconds."""
        self.set('API', 'timeout', value)
    
    @property
    def app_name(self) -> str:
        """Get the application name."""
        return self.get('Application', 'app_name', 'Chemical Equipment Analytics')
    
    @property
    def window_width(self) -> int:
        """Get the default window width."""
        return self.get_int('Application', 'window_width', 1200)
    
    @property
    def window_height(self) -> int:
        """Get the default window height."""
        return self.get_int('Application', 'window_height', 800)
    
    @property
    def max_file_size_mb(self) -> int:
        """Get the maximum file size for uploads in MB."""
        return self.get_int('Application', 'max_file_size_mb', 10)
    
    @property
    def page_size(self) -> int:
        """Get the default page size for data tables."""
        return self.get_int('Data', 'page_size', 50)
    
    @property
    def default_chart_type(self) -> str:
        """Get the default chart type."""
        return self.get('Data', 'default_chart_type', 'bar')
    
    @property
    def temp_dir(self) -> Path:
        """Get the temporary files directory path."""
        temp_path = self.get('Paths', 'temp_dir', 'temp')
        return Path(temp_path)
    
    @property
    def reports_dir(self) -> Path:
        """Get the reports directory path."""
        reports_path = self.get('Paths', 'reports_dir', 'reports')
        return Path(reports_path)


# Global configuration instance
_config_instance: Optional[Config] = None


def get_config(config_file: Optional[str] = None) -> Config:
    """
    Get the global configuration instance.
    
    Args:
        config_file: Path to config file (only used on first call)
        
    Returns:
        Config instance
    """
    global _config_instance
    
    if _config_instance is None:
        _config_instance = Config(config_file)
    
    return _config_instance


def reset_config():
    """Reset the global configuration instance (mainly for testing)."""
    global _config_instance
    _config_instance = None
