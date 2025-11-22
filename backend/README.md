# Chemical Equipment Analytics - Backend

Django REST API backend for the Chemical Equipment Analytics application.

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
  ```bash
  venv\Scripts\activate
  ```
- macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

3. Install dependencies:
```bash
pip install -r ../requirements.txt
```

4. Run database migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser (optional, for admin access):
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

## Project Structure

```
backend/
├── chemical_equipment_analytics/  # Main project configuration
│   ├── __init__.py
│   ├── settings.py               # Django settings
│   ├── urls.py                   # Root URL configuration
│   ├── wsgi.py                   # WSGI configuration
│   └── asgi.py                   # ASGI configuration
├── api/                          # Main API application
│   ├── __init__.py
│   ├── models.py                 # Database models
│   ├── serializers.py            # DRF serializers
│   ├── views.py                  # API views
│   ├── urls.py                   # API URL routing
│   ├── admin.py                  # Django admin configuration
│   ├── apps.py                   # App configuration
│   ├── tests.py                  # Unit tests
│   └── services/                 # Service layer (to be implemented)
│       └── __init__.py
├── manage.py                     # Django management script
└── README.md                     # This file
```

## API Documentation

For comprehensive API documentation including:
- Detailed endpoint descriptions
- Request/response formats
- Authentication details
- Error handling
- Code examples

See **[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)**

### Quick Reference - API Endpoints

#### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/register/` - User registration
- `POST /api/auth/logout/` - User logout

#### Datasets
- `GET /api/datasets/` - List datasets (last 5)
- `POST /api/datasets/upload/` - Upload CSV file
- `GET /api/datasets/{id}/` - Retrieve dataset details
- `GET /api/datasets/{id}/data/` - Get equipment records (paginated)
- `GET /api/datasets/{id}/summary/` - Get summary statistics
- `GET /api/datasets/{id}/report/` - Generate PDF report
- `DELETE /api/datasets/{id}/` - Delete dataset

### Browsable API

Django REST Framework provides an interactive browsable API. Access it by:
1. Starting the development server: `python manage.py runserver`
2. Navigating to `http://localhost:8000/api/` in your browser
3. Logging in with your credentials

The browsable API allows you to explore endpoints, view documentation, and test API calls directly from your browser.

## Sample Data

A sample CSV file is provided for testing and demonstration purposes:

**Location:** `backend/sample_equipment_data.csv`

This file contains 15 equipment records with the following structure:
- Equipment Name
- Type (Pump, Reactor, Heat Exchanger, Compressor)
- Flowrate (L/min)
- Pressure (bar)
- Temperature (°C)

You can use this file to test the CSV upload functionality through either the web or desktop frontend.

## Database

The application uses SQLite for development. The database file (`db.sqlite3`) will be created automatically when you run migrations.

## Configuration

Key settings are configured in `chemical_equipment_analytics/settings.py`:
- Database: SQLite (default)
- REST Framework with Token Authentication
- CORS enabled for React development server (localhost:3000)
- Pagination: 100 items per page

## Next Steps

After completing this setup, you can proceed with implementing:
1. CSV processing service
2. Analytics service
3. PDF generation service
4. Additional API endpoints for file upload and report generation
