# Design Document

## Overview

The Chemical Equipment Analytics Application is a hybrid system with a unified Django REST API backend serving two distinct frontends: a React web application and a PyQt5 desktop application. The architecture follows a client-server model where both clients consume the same RESTful API endpoints for data upload, retrieval, analysis, and report generation.

## Architecture

### High-Level Architecture

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
         │  - REST Framework      │
         │  - Authentication      │
         │  - File Processing     │
         │  - PDF Generation      │
         └───────────┬────────────┘
                     │
         ┌───────────▼────────────┐
         │   SQLite Database      │
         │  - Datasets            │
         │  - Equipment Records   │
         │  - Users               │
         └────────────────────────┘
```

### Technology Stack

**Backend:**
- Django 4.x with Django REST Framework
- Pandas for CSV processing and analytics
- ReportLab for PDF generation
- SQLite for data persistence
- Token-based authentication (DRF TokenAuthentication)

**Web Frontend:**
- React 18.x with functional components and hooks
- Axios for API communication
- Chart.js with react-chartjs-2 for visualizations
- CSS modules or Tailwind CSS for styling

**Desktop Frontend:**
- PyQt5 for GUI framework
- Matplotlib for chart rendering
- Requests library for API communication
- QTableWidget for data display

## Components and Interfaces

### Backend Components

#### 1. API Endpoints

**Authentication:**
- `POST /api/auth/login/` - User login, returns authentication token
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/register/` - User registration (optional)

**Dataset Management:**
- `POST /api/datasets/upload/` - Upload CSV file
- `GET /api/datasets/` - List all datasets (last 5)
- `GET /api/datasets/{id}/` - Retrieve specific dataset details
- `GET /api/datasets/{id}/data/` - Retrieve equipment records for dataset
- `DELETE /api/datasets/{id}/` - Delete a dataset

**Analytics:**
- `GET /api/datasets/{id}/summary/` - Get summary statistics
- `GET /api/datasets/{id}/report/` - Generate and download PDF report

**Sample Data:**
- `GET /api/sample-data/` - Download sample CSV file

#### 2. Django Models

**User Model:**
- Uses Django's built-in User model
- Extended with authentication tokens

**Dataset Model:**
```python
- id: AutoField (primary key)
- name: CharField (derived from filename)
- uploaded_at: DateTimeField
- uploaded_by: ForeignKey(User)
- total_records: IntegerField
- avg_flowrate: FloatField
- avg_pressure: FloatField
- avg_temperature: FloatField
- type_distribution: JSONField
```

**EquipmentRecord Model:**
```python
- id: AutoField (primary key)
- dataset: ForeignKey(Dataset)
- equipment_name: CharField
- equipment_type: CharField
- flowrate: FloatField
- pressure: FloatField
- temperature: FloatField
```

#### 3. Service Layer

**CSVProcessor Service:**
- Validates CSV structure
- Parses CSV using Pandas
- Extracts and validates data types
- Returns structured data or validation errors

**AnalyticsService:**
- Calculates summary statistics
- Computes averages for numeric fields
- Generates type distribution
- Prepares data for visualization

**PDFGenerator Service:**
- Creates PDF reports using ReportLab
- Embeds summary statistics
- Includes charts as images
- Formats data tables

**HistoryManager Service:**
- Maintains last 5 datasets
- Removes oldest when limit exceeded
- Handles cascade deletion of equipment records

### Frontend Components (Web)

#### React Component Structure

```
src/
├── components/
│   ├── Auth/
│   │   ├── Login.jsx
│   │   └── PrivateRoute.jsx
│   ├── Upload/
│   │   └── FileUpload.jsx
│   ├── Dashboard/
│   │   ├── Dashboard.jsx
│   │   ├── DataTable.jsx
│   │   ├── SummaryStats.jsx
│   │   └── Charts.jsx
│   ├── History/
│   │   └── DatasetHistory.jsx
│   └── Reports/
│       └── PDFDownload.jsx
├── services/
│   └── api.js
├── utils/
│   └── auth.js
└── App.jsx
```

**Key Components:**
- **Login**: Authentication form with token storage
- **FileUpload**: Drag-and-drop or file selector for CSV upload
- **Dashboard**: Main view showing current dataset analysis
- **DataTable**: Paginated table of equipment records
- **SummaryStats**: Display cards for key metrics
- **Charts**: Chart.js visualizations (bar chart for type distribution, line charts for trends)
- **DatasetHistory**: List of previous uploads with selection capability
- **PDFDownload**: Button to trigger report generation

### Frontend Components (Desktop)

#### PyQt5 Application Structure

```
desktop_app/
├── main.py
├── ui/
│   ├── main_window.py
│   ├── login_dialog.py
│   ├── upload_widget.py
│   ├── data_table_widget.py
│   ├── summary_widget.py
│   ├── chart_widget.py
│   └── history_widget.py
├── services/
│   └── api_client.py
└── utils/
    └── config.py
```

**Key Windows/Widgets:**
- **MainWindow**: QMainWindow with menu bar and central widget
- **LoginDialog**: QDialog for authentication
- **UploadWidget**: File selection and upload progress
- **DataTableWidget**: QTableWidget for equipment records
- **SummaryWidget**: QGroupBox with QLabel elements for statistics
- **ChartWidget**: QWidget with embedded Matplotlib canvas
- **HistoryWidget**: QListWidget for dataset selection

## Data Models

### CSV File Format

```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A1,Pump,150.5,45.2,85.0
Reactor-B2,Reactor,200.0,120.5,350.0
Heat-Exchanger-C3,Heat Exchanger,180.3,30.0,150.5
```

**Validation Rules:**
- Required columns: Equipment Name, Type, Flowrate, Pressure, Temperature
- Flowrate: Positive float (units: L/min)
- Pressure: Positive float (units: bar)
- Temperature: Float (units: °C)
- Equipment Name: Non-empty string
- Type: Non-empty string

### API Response Formats

**Dataset Summary Response:**
```json
{
  "id": 1,
  "name": "equipment_data_2025.csv",
  "uploaded_at": "2025-11-19T10:30:00Z",
  "total_records": 25,
  "avg_flowrate": 175.5,
  "avg_pressure": 65.3,
  "avg_temperature": 195.2,
  "type_distribution": {
    "Pump": 8,
    "Reactor": 6,
    "Heat Exchanger": 7,
    "Compressor": 4
  }
}
```

**Equipment Records Response:**
```json
{
  "count": 25,
  "results": [
    {
      "id": 1,
      "equipment_name": "Pump-A1",
      "equipment_type": "Pump",
      "flowrate": 150.5,
      "pressure": 45.2,
      "temperature": 85.0
    }
  ]
}
```

## Error Handling

### Backend Error Responses

**Standard Error Format:**
```json
{
  "error": "Error type",
  "message": "Detailed error message",
  "details": {}
}
```

**Error Scenarios:**
1. **Invalid CSV Format** (400 Bad Request)
   - Missing required columns
   - Invalid data types
   - Empty file

2. **Authentication Errors** (401 Unauthorized)
   - Invalid credentials
   - Expired token
   - Missing token

3. **Not Found** (404 Not Found)
   - Dataset does not exist
   - Invalid endpoint

4. **Server Errors** (500 Internal Server Error)
   - Database connection issues
   - PDF generation failures
   - Unexpected exceptions

### Frontend Error Handling

**Web Frontend:**
- Display error messages using toast notifications or alert components
- Form validation before submission
- Loading states during API calls
- Retry mechanisms for failed requests

**Desktop Frontend:**
- QMessageBox for error dialogs
- Status bar messages for non-critical errors
- Progress dialogs for long operations
- Graceful degradation when API is unavailable

## Testing Strategy

### Backend Testing

**Unit Tests:**
- Model validation and methods
- CSV parsing logic
- Analytics calculations
- PDF generation functions

**Integration Tests:**
- API endpoint responses
- Authentication flow
- Database operations
- File upload processing

**Test Data:**
- Valid CSV samples with various equipment types
- Invalid CSV samples (missing columns, wrong types)
- Edge cases (empty files, very large files)

### Frontend Testing (Web)

**Component Tests:**
- React component rendering
- User interaction handling
- API service mocking
- Chart rendering

**E2E Tests (Optional):**
- Complete upload workflow
- Authentication flow
- Dataset history navigation

### Frontend Testing (Desktop)

**Widget Tests:**
- PyQt5 widget initialization
- Signal/slot connections
- API client mocking
- Chart generation

**Manual Testing:**
- Cross-platform compatibility (Windows, macOS, Linux)
- UI responsiveness
- File dialog functionality

## Deployment Considerations

### Backend Deployment

**Development:**
- Django development server on localhost:8000
- SQLite database in project directory
- CORS enabled for React development server

**Production (Optional):**
- Gunicorn or uWSGI application server
- Nginx reverse proxy
- PostgreSQL database migration
- Static file serving
- HTTPS configuration

### Frontend Deployment

**Web Application:**
- Development: React development server (localhost:3000)
- Production: Build static files and serve via Nginx or CDN
- Environment variables for API endpoint configuration

**Desktop Application:**
- Package using PyInstaller or cx_Freeze
- Include Python runtime and dependencies
- Configuration file for API endpoint
- Installer creation for target platforms

## Security Considerations

1. **Authentication:**
   - Token-based authentication with secure token generation
   - HTTPS for production deployments
   - Token expiration and refresh mechanisms

2. **File Upload:**
   - File size limits (e.g., 10MB maximum)
   - File type validation (CSV only)
   - Sanitize filenames
   - Virus scanning (optional)

3. **Data Access:**
   - Users can only access their own datasets
   - Admin users can access all datasets (optional)
   - Rate limiting on API endpoints

4. **Input Validation:**
   - Validate all CSV data before database insertion
   - Prevent SQL injection through ORM usage
   - Sanitize user inputs

## Performance Optimization

1. **Database:**
   - Index on dataset.uploaded_at for history queries
   - Index on equipment_record.dataset_id for joins
   - Pagination for large datasets

2. **API:**
   - Caching for summary statistics
   - Compression for large responses
   - Async processing for PDF generation

3. **Frontend:**
   - Lazy loading for charts
   - Virtual scrolling for large tables
   - Debouncing for search/filter operations
