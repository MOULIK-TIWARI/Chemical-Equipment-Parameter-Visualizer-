# Configuration Management Guide

## Overview

The Chemical Equipment Analytics Desktop Application uses a centralized configuration management system to handle application settings. Configuration is stored in `config.ini` and accessed through the `utils.config` module.

## Configuration File

The configuration file (`config.ini`) is located in the `desktop_app` directory and uses the INI file format with sections and key-value pairs.

### Default Configuration

```ini
[API]
# Base URL for the Django REST API backend
base_url = http://localhost:8000/api

# Request timeout in seconds
timeout = 30

[Application]
# Application name
app_name = Chemical Equipment Analytics

# Default window size (width x height)
window_width = 1200
window_height = 800

# Maximum file size for CSV uploads (in MB)
max_file_size_mb = 10

[Data]
# Number of records to display per page in tables
page_size = 50

# Default chart type for visualizations
default_chart_type = bar

[Paths]
# Directory for storing temporary files
temp_dir = temp

# Directory for downloaded reports
reports_dir = reports
```

## Usage

### Basic Usage

```python
from utils.config import get_config

# Get the global configuration instance
config = get_config()

# Access configuration values using properties
api_url = config.api_base_url
timeout = config.api_timeout
window_width = config.window_width
```

### Using with API Client

```python
from services.api_client import APIClient
from utils.config import get_config

# Load configuration
config = get_config()

# Initialize API client with configured values
client = APIClient(
    base_url=config.api_base_url,
    timeout=config.api_timeout
)
```

### Reading Configuration Values

The `Config` class provides several methods for reading values:

```python
# Get string value
value = config.get('Section', 'key', fallback='default')

# Get integer value
int_value = config.get_int('Section', 'key', fallback=0)

# Get float value
float_value = config.get_float('Section', 'key', fallback=0.0)

# Get boolean value
bool_value = config.get_bool('Section', 'key', fallback=False)
```

### Setting Configuration Values

```python
# Set a configuration value
config.set('API', 'base_url', 'http://example.com/api')

# Or use properties
config.api_base_url = 'http://example.com/api'
config.api_timeout = 60

# Save changes to file
config.save()
```

### Available Properties

The `Config` class provides convenient properties for commonly used settings:

#### API Settings
- `api_base_url` - Base URL for the API (default: `http://localhost:8000/api`)
- `api_timeout` - Request timeout in seconds (default: `30`)

#### Application Settings
- `app_name` - Application name (default: `Chemical Equipment Analytics`)
- `window_width` - Default window width (default: `1200`)
- `window_height` - Default window height (default: `800`)
- `max_file_size_mb` - Maximum file size for uploads in MB (default: `10`)

#### Data Settings
- `page_size` - Default page size for data tables (default: `50`)
- `default_chart_type` - Default chart type (default: `bar`)

#### Path Settings
- `temp_dir` - Temporary files directory (default: `temp`)
- `reports_dir` - Reports directory (default: `reports`)

## Customization

### Changing API Server

To connect to a different API server, edit the `config.ini` file:

```ini
[API]
base_url = http://production-server.com/api
timeout = 60
```

Or programmatically:

```python
config = get_config()
config.api_base_url = 'http://production-server.com/api'
config.save()
```

### Adjusting Window Size

```ini
[Application]
window_width = 1600
window_height = 900
```

### Changing Data Display Settings

```ini
[Data]
page_size = 100
default_chart_type = line
```

## File Location

The configuration file is automatically created in the `desktop_app` directory if it doesn't exist. The default location is:

```
desktop_app/
├── config.ini          # Configuration file
├── utils/
│   └── config.py       # Configuration management module
└── ...
```

## Environment-Specific Configuration

For different environments (development, testing, production), you can:

1. **Use different config files:**
   ```python
   config = get_config(config_file='config.production.ini')
   ```

2. **Create environment-specific config files:**
   - `config.dev.ini` - Development settings
   - `config.test.ini` - Testing settings
   - `config.prod.ini` - Production settings

3. **Load based on environment variable:**
   ```python
   import os
   env = os.getenv('APP_ENV', 'dev')
   config = get_config(config_file=f'config.{env}.ini')
   ```

## Best Practices

1. **Don't commit sensitive data** - If you add passwords or API keys to the config, add `config.ini` to `.gitignore`

2. **Use defaults** - Always provide sensible defaults in the code

3. **Validate values** - Validate configuration values before using them:
   ```python
   timeout = max(1, min(config.api_timeout, 300))  # Clamp between 1-300 seconds
   ```

4. **Document changes** - If you add new configuration options, document them in this guide

5. **Use properties** - For commonly used settings, add properties to the `Config` class for easier access

## Troubleshooting

### Configuration file not found

If the configuration file doesn't exist, it will be automatically created with default values.

### Invalid values

If a configuration value is invalid (e.g., non-numeric value for an integer setting), the fallback/default value will be used.

### Permission errors

If the application cannot write to the configuration file, check file permissions and ensure the directory is writable.

## Requirements

This configuration system satisfies **Requirement 1.2**: The Desktop Frontend needs configurable API connection settings.
