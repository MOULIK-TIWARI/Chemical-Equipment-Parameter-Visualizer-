# Chemical Equipment Analytics - Desktop Application

PyQt5-based desktop application for chemical equipment data analysis.

## Project Structure

```
desktop_app/
├── main.py                      # Application entry point
├── config.ini                   # Configuration file
├── requirements.txt             # Python dependencies
├── test_api_client.py          # API client test script
├── API_CLIENT_USAGE.md         # API client documentation
├── CONFIGURATION_GUIDE.md      # Configuration system documentation
├── ui/                         # UI components and windows
│   └── __init__.py
├── services/                   # API client and business logic
│   ├── __init__.py
│   └── api_client.py          # Complete API client implementation
└── utils/                      # Configuration and utilities
    ├── __init__.py
    └── config.py               # Configuration management
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure the Django backend is running:
```bash
cd ../backend
python manage.py runserver
```

3. Run the application:
```bash
python main.py
```

## Requirements

- Python 3.8+
- PyQt5 5.15.0+
- matplotlib 3.5.0+
- requests 2.28.0+
- numpy 1.21.0+

## API Client

The application includes a comprehensive API client (`services/api_client.py`) that handles all communication with the Django REST API backend.

### Features

- **Authentication**: Login, register, logout with automatic token management
- **Dataset Management**: Upload CSV files, retrieve datasets, get equipment records
- **Analytics**: Fetch summary statistics and type distributions
- **Report Generation**: Download PDF reports
- **Error Handling**: Comprehensive exception handling for network and API errors
- **Token Persistence**: Automatic token storage and retrieval across sessions

### Quick Start

```python
from services.api_client import APIClient

# Initialize client
client = APIClient()

# Login
client.login(username="user", password="pass")

# Upload dataset
dataset = client.upload_dataset("data.csv")

# Get summary
summary = client.get_dataset_summary(dataset['id'])

# Download report
client.download_report(dataset['id'], "report.pdf")
```

For complete API client documentation, see [API_CLIENT_USAGE.md](API_CLIENT_USAGE.md).

### Testing the API Client

Run the test script to verify the API client functionality:

```bash
python test_api_client.py
```

## Configuration

The application uses a centralized configuration management system. Settings are stored in `config.ini` and accessed through the `utils.config` module.

### Configuration File

The `config.ini` file is automatically created with default values on first run. You can customize settings such as:

- **API Settings**: Base URL, timeout
- **Application Settings**: Window size, max file size
- **Data Settings**: Page size, default chart type
- **Paths**: Temporary files, reports directory

### Using Configuration

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

### Changing API Server

Edit `config.ini`:

```ini
[API]
base_url = http://your-server.com/api
timeout = 30
```

For complete configuration documentation, see [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md).

## Features

### Authentication
- Login dialog with username/password authentication
- Automatic token management and persistence
- Secure logout functionality

### File Upload
- CSV file selection with file dialog
- File validation and error handling
- Progress indication during upload
- Automatic navigation to dashboard after upload
- Comprehensive error messages for validation, network, and API errors

### Main Window
- Tab-based interface (Upload, Dashboard, History)
- Menu bar with File and Help menus
- Status bar for application messages
- Keyboard shortcuts for common actions

## UI Components

### Login Dialog
The login dialog provides secure authentication before accessing the application.

See [LOGIN_DIALOG_USAGE.md](LOGIN_DIALOG_USAGE.md) for details.

### Upload Widget
The upload widget allows users to select and upload CSV files containing equipment data.

Features:
- File selection with CSV filter
- File information display
- Upload progress indication
- Success/error message display
- Automatic dashboard navigation

See [UPLOAD_WIDGET_USAGE.md](UPLOAD_WIDGET_USAGE.md) for details.

### Main Window
The main window provides the primary application interface with tabs for different views.

See [MAIN_WINDOW_IMPLEMENTATION.md](MAIN_WINDOW_IMPLEMENTATION.md) for details.

## Testing

### Run All Tests

```bash
# API Client tests
python test_api_client.py

# Configuration tests
python test_config.py

# Login dialog tests
python test_login_dialog.py

# Upload widget tests
python test_upload_widget.py

# Upload integration tests
python test_upload_integration.py

# Main window tests
python test_main_window.py
```

### Demo Applications

```bash
# Demo upload widget
python demo_upload_widget.py
```

## Development Status

### Completed ✅
- ✅ Project structure initialization
- ✅ API client implementation with full endpoint coverage
- ✅ Authentication and token management
- ✅ Error handling and network resilience
- ✅ Configuration management system
- ✅ Login dialog implementation
- ✅ Main window with tab interface
- ✅ File upload widget with validation
- ✅ Dashboard widgets (summary, table, charts)
- ✅ History widget for dataset navigation
- ✅ Chart visualization with Matplotlib
- ✅ Data table with sorting
- ✅ PDF report download functionality
- ✅ Complete dashboard integration
- ✅ Chart widget error handling (Singular matrix fix)

### Status
**Production Ready** - All features implemented and tested
