# API Client Usage Guide

This document provides comprehensive documentation for using the `APIClient` class in the Chemical Equipment Analytics Desktop Application.

## Overview

The `APIClient` class provides a complete interface for communicating with the Django REST API backend. It handles authentication, token management, and all API endpoint interactions with proper error handling.

## Installation

Ensure the required dependencies are installed:

```bash
pip install -r requirements.txt
```

## Basic Usage

### Initialization

```python
from services.api_client import APIClient

# Initialize with default settings (localhost:8000)
client = APIClient()

# Or specify a custom base URL
client = APIClient(base_url="http://api.example.com/api")

# Set custom timeout (default is 30 seconds)
client = APIClient(timeout=60)
```

### Using Configuration Management

The recommended way to initialize the API client is to use the configuration management system:

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

This approach allows you to manage API settings centrally in the `config.ini` file. See `CONFIGURATION_GUIDE.md` for more details.

### Configuration

```python
# Update base URL
client.set_base_url("http://localhost:8000/api")

# Update timeout
client.set_timeout(60)

# Check connection status
status = client.get_connection_status()
print(f"Connected: {status['connected']}")
print(f"Message: {status['message']}")
```

## Authentication

### Login

```python
from services.api_client import APIClient, AuthenticationError

client = APIClient()

try:
    response = client.login(username="user123", password="password123")
    print(f"Login successful!")
    print(f"Token: {response['token']}")
    print(f"User ID: {response['user_id']}")
    print(f"Username: {response['username']}")
except AuthenticationError as e:
    print(f"Login failed: {e}")
```

### Register

```python
try:
    response = client.register(
        username="newuser",
        password="securepass",
        email="user@example.com"
    )
    print(f"Registration successful!")
    print(f"Token: {response['token']}")
except ValidationError as e:
    print(f"Registration failed: {e}")
```

### Logout

```python
try:
    response = client.logout()
    print(f"Logout successful: {response['message']}")
except AuthenticationError as e:
    print(f"Logout failed: {e}")
```

### Check Authentication Status

```python
if client.is_authenticated():
    print("User is authenticated")
else:
    print("User is not authenticated")
```

## Dataset Management

### Upload CSV File

```python
from services.api_client import ValidationError

try:
    response = client.upload_dataset(file_path="path/to/equipment_data.csv")
    print(f"Upload successful!")
    print(f"Dataset ID: {response['id']}")
    print(f"Dataset Name: {response['name']}")
    print(f"Total Records: {response['total_records']}")
except ValidationError as e:
    print(f"CSV validation failed: {e}")
except FileNotFoundError as e:
    print(f"File not found: {e}")
```

### Get Dataset List (Last 5)

```python
try:
    datasets = client.get_datasets()
    print(f"Found {len(datasets)} datasets:")
    for dataset in datasets:
        print(f"  - {dataset['name']} (ID: {dataset['id']})")
        print(f"    Uploaded: {dataset['uploaded_at']}")
        print(f"    Records: {dataset['total_records']}")
except AuthenticationError as e:
    print(f"Authentication required: {e}")
```

### Get Dataset Details

```python
try:
    dataset = client.get_dataset(dataset_id=1)
    print(f"Dataset: {dataset['name']}")
    print(f"Total Records: {dataset['total_records']}")
    print(f"Average Flowrate: {dataset['avg_flowrate']}")
    print(f"Average Pressure: {dataset['avg_pressure']}")
    print(f"Average Temperature: {dataset['avg_temperature']}")
except APIClientError as e:
    print(f"Error: {e}")
```

### Get Dataset Equipment Records

```python
try:
    # Get first page (50 records)
    data = client.get_dataset_data(dataset_id=1)
    print(f"Total records: {data['count']}")
    print(f"Records on this page: {len(data['results'])}")
    
    for record in data['results']:
        print(f"  - {record['equipment_name']}: {record['equipment_type']}")
        print(f"    Flowrate: {record['flowrate']}, Pressure: {record['pressure']}")
    
    # Get specific page with custom page size
    data = client.get_dataset_data(dataset_id=1, page=2, page_size=100)
    
except APIClientError as e:
    print(f"Error: {e}")
```

### Get Dataset Summary Statistics

```python
try:
    summary = client.get_dataset_summary(dataset_id=1)
    print(f"Dataset: {summary['name']}")
    print(f"Total Records: {summary['total_records']}")
    print(f"Averages:")
    print(f"  Flowrate: {summary['avg_flowrate']:.2f}")
    print(f"  Pressure: {summary['avg_pressure']:.2f}")
    print(f"  Temperature: {summary['avg_temperature']:.2f}")
    print(f"Type Distribution:")
    for equipment_type, count in summary['type_distribution'].items():
        print(f"  {equipment_type}: {count}")
except APIClientError as e:
    print(f"Error: {e}")
```

### Delete Dataset

```python
try:
    client.delete_dataset(dataset_id=1)
    print("Dataset deleted successfully")
except APIClientError as e:
    print(f"Error: {e}")
```

## Report Generation

### Download PDF Report

```python
try:
    save_path = client.download_report(
        dataset_id=1,
        save_path="reports/equipment_report.pdf"
    )
    print(f"Report saved to: {save_path}")
except APIClientError as e:
    print(f"Error generating report: {e}")
```

## Error Handling

The API client provides specific exception types for different error scenarios:

### Exception Hierarchy

```
APIClientError (base exception)
├── AuthenticationError (401 errors)
├── ValidationError (400 errors)
└── NetworkError (connection/timeout errors)
```

### Comprehensive Error Handling Example

```python
from services.api_client import (
    APIClient,
    APIClientError,
    AuthenticationError,
    ValidationError,
    NetworkError
)

client = APIClient()

try:
    # Attempt to upload a file
    response = client.upload_dataset("data.csv")
    print("Upload successful!")
    
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
    # Prompt user to login
    
except ValidationError as e:
    print(f"CSV validation failed: {e}")
    # Show validation errors to user
    
except NetworkError as e:
    print(f"Network error: {e}")
    # Check internet connection or server status
    
except FileNotFoundError as e:
    print(f"File not found: {e}")
    # Prompt user to select a valid file
    
except APIClientError as e:
    print(f"API error: {e}")
    # Handle other API errors
    
except Exception as e:
    print(f"Unexpected error: {e}")
    # Handle unexpected errors
```

## Token Persistence

The API client automatically saves and loads authentication tokens:

- Tokens are saved to: `~/.chemical_equipment_analytics/token.txt`
- Tokens are automatically loaded on client initialization
- Tokens are cleared on logout

This means users don't need to login every time they start the application.

## Complete Example: Upload and Generate Report

```python
from services.api_client import APIClient, APIClientError
from utils.config import get_config

def main():
    # Load configuration and initialize client
    config = get_config()
    client = APIClient(
        base_url=config.api_base_url,
        timeout=config.api_timeout
    )
    
    # Check if already authenticated
    if not client.is_authenticated():
        # Login
        try:
            client.login(username="user123", password="password123")
            print("Login successful!")
        except APIClientError as e:
            print(f"Login failed: {e}")
            return
    
    # Upload CSV file
    try:
        dataset = client.upload_dataset("equipment_data.csv")
        dataset_id = dataset['id']
        print(f"Uploaded dataset: {dataset['name']}")
        print(f"Total records: {dataset['total_records']}")
    except APIClientError as e:
        print(f"Upload failed: {e}")
        return
    
    # Get summary statistics
    try:
        summary = client.get_dataset_summary(dataset_id)
        print(f"\nSummary Statistics:")
        print(f"  Average Flowrate: {summary['avg_flowrate']:.2f}")
        print(f"  Average Pressure: {summary['avg_pressure']:.2f}")
        print(f"  Average Temperature: {summary['avg_temperature']:.2f}")
    except APIClientError as e:
        print(f"Failed to get summary: {e}")
    
    # Download PDF report
    try:
        report_path = client.download_report(
            dataset_id=dataset_id,
            save_path=f"report_{dataset_id}.pdf"
        )
        print(f"\nReport saved to: {report_path}")
    except APIClientError as e:
        print(f"Failed to generate report: {e}")

if __name__ == "__main__":
    main()
```

## Testing

To test the API client, ensure the Django backend is running:

```bash
# In the backend directory
python manage.py runserver
```

Then run the test script:

```bash
# In the desktop_app directory
python test_api_client.py
```

## Requirements Mapping

This API client implementation satisfies the following requirements:

- **Requirement 1.2**: Desktop frontend file upload to backend API
- **Requirement 2.5**: Desktop frontend requests summary statistics from backend
- **Requirement 4.4**: Desktop frontend requests dataset history from backend
- **Requirement 5.2**: Desktop frontend requests PDF report generation from backend

## Notes

- All methods that communicate with the API may raise `NetworkError` if the server is unreachable
- Authentication is required for all dataset and report operations
- The client automatically includes the authentication token in requests when available
- File uploads support CSV files only (validated by the backend)
- PDF reports are streamed and saved to disk to handle large files efficiently
