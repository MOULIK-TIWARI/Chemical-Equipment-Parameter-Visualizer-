# Chemical Equipment Analytics Application

A hybrid application for visualizing and analyzing chemical equipment data. The system consists of a Django REST API backend serving both a React web frontend and a PyQt5 desktop application.

## Overview

This application allows users to:
- Upload CSV files containing chemical equipment data
- View summary statistics and analytics
- Visualize data through interactive charts and tables
- Access historical datasets (last 5 uploads)
- Generate and download PDF reports
- Access the system via web browser or desktop application

## Architecture

```
┌─────────────────┐         ┌─────────────────┐
│  React Web App  │         │ PyQt5 Desktop   │
│  (Port 3000)    │         │  Application    │
└────────┬────────┘         └────────┬────────┘
         │                           │
         │    HTTP/REST API          │
         └───────────┬───────────────┘
                     │
         ┌───────────▼────────────┐
         │   Django Backend       │
         │   (Port 8000)          │
         └───────────┬────────────┘
                     │
         ┌───────────▼────────────┐
         │   SQLite Database      │
         └────────────────────────┘
```

## Technology Stack

- **Backend**: Django 4.x, Django REST Framework, Pandas, ReportLab
- **Web Frontend**: React 18.x, Axios, Chart.js
- **Desktop Frontend**: PyQt5, Matplotlib, Requests
- **Database**: SQLite

## Prerequisites

- Python 3.8 or higher
- Node.js 16.x or higher (for web frontend)
- pip (Python package manager)
- npm or yarn (for web frontend)

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run database migrations:
```bash
python manage.py migrate
```

5. Create a superuser (optional, for admin access):
```bash
python manage.py createsuperuser
```

6. Start the development server:
```bash
python manage.py runserver
```

The backend API will be available at `http://localhost:8000`

### React Web Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Configure the API endpoint (if needed):
   - Edit `frontend/src/services/api.js`
   - Update the `baseURL` if your backend is not running on `http://localhost:8000`

4. Start the development server:
```bash
npm run dev
# or
yarn dev
```

The web application will be available at `http://localhost:3000`

### PyQt5 Desktop Application Setup

1. Navigate to the desktop_app directory:
```bash
cd desktop_app
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure the API endpoint:
   - Edit `desktop_app/config.ini`
   - Update the `api_base_url` if your backend is not running on `http://localhost:8000`

5. Run the application:
```bash
python main.py
```

## CSV File Format

The application expects CSV files with the following columns:

```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A1,Pump,150.5,45.2,85.0
Reactor-B2,Reactor,200.0,120.5,350.0
Heat-Exchanger-C3,Heat Exchanger,180.3,30.0,150.5
```

**Column Requirements:**
- **Equipment Name**: Non-empty string
- **Type**: Non-empty string (e.g., Pump, Reactor, Heat Exchanger, Compressor)
- **Flowrate**: Positive float (units: L/min)
- **Pressure**: Positive float (units: bar)
- **Temperature**: Float (units: °C)

A sample CSV file is provided at `backend/sample_equipment_data.csv`

## Features

### Web Frontend Features
- User authentication with token-based sessions
- Drag-and-drop CSV file upload
- Interactive dashboard with summary statistics
- Data table with sorting and pagination
- Interactive charts using Chart.js
- Dataset history browser
- PDF report generation and download
- Error handling with toast notifications

### Desktop Application Features
- User authentication dialog
- File browser for CSV upload
- Dashboard with summary statistics widgets
- Data table with sorting capabilities
- Charts using Matplotlib
- Dataset history list
- PDF report download with save dialog
- Native error dialogs and status messages

## Testing

### Backend Tests
```bash
cd backend
python manage.py test
```

### Frontend Tests
```bash
cd frontend
npm test
# or
yarn test
```

### Desktop Application Tests
```bash
cd desktop_app
python -m pytest
```

## Project Structure

```
.
├── backend/                    # Django REST API
│   ├── api/                   # Main API application
│   │   ├── models.py         # Database models
│   │   ├── views.py          # API endpoints
│   │   ├── serializers.py    # DRF serializers
│   │   ├── services/         # Business logic
│   │   └── tests.py          # Unit tests
│   ├── chemical_equipment_analytics/  # Django project settings
│   ├── manage.py
│   └── requirements.txt
├── frontend/                   # React web application
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── services/         # API client
│   │   └── utils/            # Utility functions
│   ├── package.json
│   └── vite.config.js
├── desktop_app/               # PyQt5 desktop application
│   ├── ui/                   # UI components
│   ├── services/             # API client
│   ├── utils/                # Utilities
│   ├── main.py               # Application entry point
│   └── requirements.txt
└── README.md
```

## Configuration

### Backend Configuration
- Database: `backend/db.sqlite3` (SQLite)
- Settings: `backend/chemical_equipment_analytics/settings.py`
- CORS: Configured for development (localhost:3000)

### Web Frontend Configuration
- API endpoint: `frontend/src/services/api.js`
- Build configuration: `frontend/vite.config.js`

### Desktop Application Configuration
- API endpoint: `desktop_app/config.ini`
- Default settings: `desktop_app/utils/config.py`
