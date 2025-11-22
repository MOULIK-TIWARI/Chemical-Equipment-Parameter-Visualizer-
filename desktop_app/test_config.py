"""
Test script for configuration management system.

This script demonstrates and tests the configuration management functionality.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import Config, get_config, reset_config


def test_default_config():
    """Test that default configuration is created correctly."""
    print("=" * 60)
    print("Test 1: Default Configuration")
    print("=" * 60)
    
    # Create a temporary config for testing
    test_config_file = Path(__file__).parent / 'test_config.ini'
    
    # Remove test config if it exists
    if test_config_file.exists():
        test_config_file.unlink()
    
    # Create config with test file
    config = Config(config_file=str(test_config_file))
    
    # Test default values
    print(f"API Base URL: {config.api_base_url}")
    print(f"API Timeout: {config.api_timeout}")
    print(f"App Name: {config.app_name}")
    print(f"Window Width: {config.window_width}")
    print(f"Window Height: {config.window_height}")
    print(f"Max File Size: {config.max_file_size_mb} MB")
    print(f"Page Size: {config.page_size}")
    print(f"Default Chart Type: {config.default_chart_type}")
    print(f"Temp Dir: {config.temp_dir}")
    print(f"Reports Dir: {config.reports_dir}")
    
    # Verify file was created
    assert test_config_file.exists(), "Config file should be created"
    print("\n✓ Default configuration created successfully")
    
    # Cleanup
    test_config_file.unlink()
    print("✓ Test config file cleaned up\n")


def test_read_write_config():
    """Test reading and writing configuration values."""
    print("=" * 60)
    print("Test 2: Read/Write Configuration")
    print("=" * 60)
    
    # Create a temporary config for testing
    test_config_file = Path(__file__).parent / 'test_config.ini'
    
    # Remove test config if it exists
    if test_config_file.exists():
        test_config_file.unlink()
    
    # Create config
    config = Config(config_file=str(test_config_file))
    
    # Modify values
    print("Setting new values...")
    config.api_base_url = "http://example.com/api"
    config.api_timeout = 60
    config.set('Application', 'window_width', '1600')
    config.save()
    
    # Create new config instance to verify persistence
    config2 = Config(config_file=str(test_config_file))
    
    # Verify values were saved
    assert config2.api_base_url == "http://example.com/api", "API URL should be saved"
    assert config2.api_timeout == 60, "Timeout should be saved"
    assert config2.window_width == 1600, "Window width should be saved"
    
    print(f"API Base URL: {config2.api_base_url}")
    print(f"API Timeout: {config2.api_timeout}")
    print(f"Window Width: {config2.window_width}")
    
    print("\n✓ Configuration read/write works correctly")
    
    # Cleanup
    test_config_file.unlink()
    print("✓ Test config file cleaned up\n")


def test_global_config():
    """Test global configuration instance."""
    print("=" * 60)
    print("Test 3: Global Configuration Instance")
    print("=" * 60)
    
    # Reset global instance
    reset_config()
    
    # Get global config
    config1 = get_config()
    config2 = get_config()
    
    # Verify they're the same instance
    assert config1 is config2, "Should return same instance"
    print("✓ Global configuration returns same instance")
    
    # Modify through one reference
    config1.api_timeout = 45
    
    # Verify change is visible through other reference
    assert config2.api_timeout == 45, "Changes should be visible"
    print("✓ Changes are visible across references\n")


def test_type_conversions():
    """Test type conversion methods."""
    print("=" * 60)
    print("Test 4: Type Conversions")
    print("=" * 60)
    
    # Create a temporary config for testing
    test_config_file = Path(__file__).parent / 'test_config.ini'
    
    # Remove test config if it exists
    if test_config_file.exists():
        test_config_file.unlink()
    
    # Create config
    config = Config(config_file=str(test_config_file))
    
    # Test integer conversion
    timeout = config.get_int('API', 'timeout')
    assert isinstance(timeout, int), "Should return integer"
    assert timeout == 30, "Should return correct value"
    print(f"✓ Integer conversion: {timeout} (type: {type(timeout).__name__})")
    
    # Test with fallback
    missing = config.get_int('NonExistent', 'key', fallback=99)
    assert missing == 99, "Should return fallback"
    print(f"✓ Fallback works: {missing}")
    
    # Test float conversion
    config.set('Test', 'float_value', '3.14')
    float_val = config.get_float('Test', 'float_value')
    assert isinstance(float_val, float), "Should return float"
    assert abs(float_val - 3.14) < 0.001, "Should return correct value"
    print(f"✓ Float conversion: {float_val} (type: {type(float_val).__name__})")
    
    # Test boolean conversion
    config.set('Test', 'bool_value', 'true')
    bool_val = config.get_bool('Test', 'bool_value')
    assert isinstance(bool_val, bool), "Should return boolean"
    assert bool_val is True, "Should return correct value"
    print(f"✓ Boolean conversion: {bool_val} (type: {type(bool_val).__name__})")
    
    print("\n✓ All type conversions work correctly")
    
    # Cleanup
    test_config_file.unlink()
    print("✓ Test config file cleaned up\n")


def test_api_client_integration():
    """Test using configuration with API client."""
    print("=" * 60)
    print("Test 5: API Client Integration")
    print("=" * 60)
    
    # Create a temporary config for testing
    test_config_file = Path(__file__).parent / 'test_config.ini'
    
    # Remove test config if it exists
    if test_config_file.exists():
        test_config_file.unlink()
    
    # Create config
    config = Config(config_file=str(test_config_file))
    
    # Import API client
    from services.api_client import APIClient
    
    # Initialize with config values
    client = APIClient(
        base_url=config.api_base_url,
        timeout=config.api_timeout
    )
    
    print(f"API Client initialized with:")
    print(f"  Base URL: {client.base_url}")
    print(f"  Timeout: {client.timeout}")
    
    # Verify values match config
    assert client.base_url == config.api_base_url, "Base URL should match config"
    assert client.timeout == config.api_timeout, "Timeout should match config"
    
    print("\n✓ API client integration works correctly")
    
    # Cleanup
    test_config_file.unlink()
    print("✓ Test config file cleaned up\n")


def main():
    """Run all configuration tests."""
    print("\n" + "=" * 60)
    print("Configuration Management System Tests")
    print("=" * 60 + "\n")
    
    try:
        test_default_config()
        test_read_write_config()
        test_global_config()
        test_type_conversions()
        test_api_client_integration()
        
        print("=" * 60)
        print("All Tests Passed! ✓")
        print("=" * 60)
        print("\nConfiguration management system is working correctly.")
        print("You can now use it in your application with:")
        print("  from utils.config import get_config")
        print("  config = get_config()")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
