# Chemical Equipment Analytics API Documentation

## Overview

This document provides comprehensive documentation for the Chemical Equipment Analytics REST API. The API is built using Django REST Framework and provides endpoints for authentication, dataset management, analytics, and report generation.

**Base URL:** `http://localhost:8000/api/`

**Authentication:** Token-based authentication (DRF TokenAuthentication)

**Content Type:** `application/json` (except file uploads which use `multipart/form-data`)

## Browsable API

Django REST Framework provides an interactive browsable API interface. You can access it by navigating to any endpoint in your web browser while logged in. The browsable API allows you to:

- View endpoint documentation
- Test API endpoints directly from the browser
- See request/response formats
- Explore available actions

To access the browsable API:
1. Start the Django development server: `python manage.py runserver`
2. Navigate to `http://localhost:8000/api/` in your browser
3. Log in using your credentials (or use session authentication)

## Authentication

All endpoints except login and register require authentication. Include the authentication token in the request header:

```
Authorization: Token <your-token-here>
```

### POST /api/auth/login/

Authenticate a user and receive an authentication token.

**Requirements:** 6.2, 6.4

**Authentication Required:** No

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Success Response (200 OK):**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user_id": 1,
  "username": "john_doe"
}
```

**Error Response (401 Unauthorized):**
```json
{
  "error": "Invalid credentials"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "password": "secure_password"}'
```

---

### POST /api/auth/register/

Register a new user account.

**Requirements:** 6.2

**Authentication Required:** No

**Request Body:**
```json
{
  "username": "string",
  "password": "string",
  "email": "string (optional)"
}
```

**Success Response (201 Created):**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user_id": 1,
  "username": "john_doe"
}
```

**Error Responses:**

**400 Bad Request** - Missing required fields:
```json
{
  "error": "Username and password are required"
}
```

**400 Bad Request** - Username already exists:
```json
{
  "error": "Username already exists"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "password": "secure_password", "email": "john@example.com"}'
```

---

### POST /api/auth/logout/

Logout the current user by deleting their authentication token.

**Requirements:** 6.5

**Authentication Required:** Yes

**Request Body:** None

**Success Response (200 OK):**
```json
{
  "message": "Successfully logged out"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

---

## Dataset Management

### POST /api/datasets/upload/

Upload a CSV file containing chemical equipment data.

**Requirements:** 1.1, 1.2, 1.3, 1.4

**Authentication Required:** Yes

**Content Type:** `multipart/form-data`

**Request Parameters:**
- `file`: CSV file (required)

**CSV File Format:**

The CSV file must contain the following columns:
- `Equipment Name` - Name of the equipment (string)
- `Type` - Equipment type (string)
- `Flowrate` - Flow rate in L/min (positive float)
- `Pressure` - Pressure in bar (positive float)
- `Temperature` - Temperature in °C (float)

**Example CSV:**
```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A1,Pump,150.5,45.2,85.0
Reactor-B2,Reactor,200.0,120.5,350.0
Heat-Exchanger-C3,Heat Exchanger,180.3,30.0,150.5
```

**Success Response (201 Created):**
```json
{
  "id": 1,
  "name": "equipment_data.csv",
  "uploaded_at": "2025-11-22T10:30:00Z",
  "uploaded_by": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  },
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

**Error Responses:**

**400 Bad Request** - No file provided:
```json
{
  "error": "No file provided",
  "message": "Please upload a CSV file using the \"file\" field"
}
```

**400 Bad Request** - Invalid file format:
```json
{
  "error": "Invalid file format",
  "message": "Only CSV files are accepted. Please upload a file with .csv extension"
}
```

**400 Bad Request** - CSV validation failed:
```json
{
  "error": "CSV validation failed",
  "message": "Missing required columns: Flowrate, Pressure"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/datasets/upload/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -F "file=@equipment_data.csv"
```

**Notes:**
- The system maintains a history of the last 5 datasets per user
- When a 6th dataset is uploaded, the oldest dataset is automatically deleted
- Summary statistics are calculated automatically upon upload

---

### GET /api/datasets/

List the last 5 datasets for the authenticated user.

**Requirements:** 4.3, 4.4

**Authentication Required:** Yes

**Query Parameters:** None

**Success Response (200 OK):**
```json
[
  {
    "id": 5,
    "name": "equipment_data_latest.csv",
    "uploaded_at": "2025-11-22T10:30:00Z",
    "uploaded_by": {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com"
    },
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
  },
  {
    "id": 4,
    "name": "equipment_data_old.csv",
    "uploaded_at": "2025-11-21T14:20:00Z",
    "uploaded_by": {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com"
    },
    "total_records": 18,
    "avg_flowrate": 160.2,
    "avg_pressure": 58.7,
    "avg_temperature": 180.5,
    "type_distribution": {
      "Pump": 6,
      "Reactor": 5,
      "Heat Exchanger": 7
    }
  }
]
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/datasets/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

---

### GET /api/datasets/{id}/

Retrieve detailed information about a specific dataset.

**Requirements:** 4.5

**Authentication Required:** Yes (must be dataset owner)

**URL Parameters:**
- `id` - Dataset ID (integer)

**Success Response (200 OK):**
```json
{
  "id": 1,
  "name": "equipment_data.csv",
  "uploaded_at": "2025-11-22T10:30:00Z",
  "uploaded_by": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  },
  "total_records": 25,
  "avg_flowrate": 175.5,
  "avg_pressure": 65.3,
  "avg_temperature": 195.2,
  "type_distribution": {
    "Pump": 8,
    "Reactor": 6,
    "Heat Exchanger": 7,
    "Compressor": 4
  },
  "records": [
    {
      "id": 1,
      "equipment_name": "Pump-A1",
      "equipment_type": "Pump",
      "flowrate": 150.5,
      "pressure": 45.2,
      "temperature": 85.0
    },
    {
      "id": 2,
      "equipment_name": "Reactor-B2",
      "equipment_type": "Reactor",
      "flowrate": 200.0,
      "pressure": 120.5,
      "temperature": 350.0
    }
  ]
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Not found."
}
```

**Error Response (403 Forbidden):**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/datasets/1/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

**Note:** For large datasets, consider using the `/api/datasets/{id}/data/` endpoint with pagination.

---

### GET /api/datasets/{id}/data/

Retrieve equipment records for a specific dataset with pagination.

**Requirements:** 4.5

**Authentication Required:** Yes (must be dataset owner)

**URL Parameters:**
- `id` - Dataset ID (integer)

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Number of records per page (default: 50, max: 1000)

**Success Response (200 OK):**
```json
{
  "count": 250,
  "next": "http://localhost:8000/api/datasets/1/data/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "equipment_name": "Pump-A1",
      "equipment_type": "Pump",
      "flowrate": 150.5,
      "pressure": 45.2,
      "temperature": 85.0
    },
    {
      "id": 2,
      "equipment_name": "Reactor-B2",
      "equipment_type": "Reactor",
      "flowrate": 200.0,
      "pressure": 120.5,
      "temperature": 350.0
    }
  ]
}
```

**Example:**
```bash
# Get first page with default page size (50)
curl -X GET http://localhost:8000/api/datasets/1/data/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"

# Get second page with custom page size (100)
curl -X GET "http://localhost:8000/api/datasets/1/data/?page=2&page_size=100" \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

---

### GET /api/datasets/{id}/summary/

Retrieve summary statistics for a specific dataset.

**Requirements:** 2.4, 2.5

**Authentication Required:** Yes (must be dataset owner)

**URL Parameters:**
- `id` - Dataset ID (integer)

**Success Response (200 OK):**
```json
{
  "id": 1,
  "name": "equipment_data.csv",
  "uploaded_at": "2025-11-22T10:30:00Z",
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

**Example:**
```bash
curl -X GET http://localhost:8000/api/datasets/1/summary/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

---

### GET /api/datasets/{id}/report/

Generate and download a PDF report for a specific dataset.

**Requirements:** 5.1, 5.2, 5.4

**Authentication Required:** Yes (must be dataset owner)

**URL Parameters:**
- `id` - Dataset ID (integer)

**Success Response (200 OK):**
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename="equipment_report_{id}_{name}"`
- Body: PDF file binary data

**PDF Report Contents:**
- Dataset information (name, ID, upload timestamp)
- Summary statistics (total count, averages)
- Equipment type distribution chart (bar chart)
- Table of equipment records (first 100 records)

**Error Response (500 Internal Server Error):**
```json
{
  "error": "PDF generation failed",
  "message": "An error occurred while generating the report: ..."
}
```

**Example:**
```bash
# Download PDF report
curl -X GET http://localhost:8000/api/datasets/1/report/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -o equipment_report.pdf

# Or open in browser (with session authentication)
# Navigate to: http://localhost:8000/api/datasets/1/report/
```

---

### DELETE /api/datasets/{id}/

Delete a specific dataset and all its equipment records.

**Authentication Required:** Yes (must be dataset owner)

**URL Parameters:**
- `id` - Dataset ID (integer)

**Success Response (204 No Content):**
- No response body

**Error Response (404 Not Found):**
```json
{
  "detail": "Not found."
}
```

**Error Response (403 Forbidden):**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/datasets/1/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

**Note:** Deleting a dataset will cascade delete all associated equipment records.

---

## Data Models

### Dataset

Represents a collection of equipment records uploaded via CSV file.

**Fields:**
- `id` (integer) - Unique identifier
- `name` (string) - Original filename of uploaded CSV
- `uploaded_at` (datetime) - Timestamp of upload (ISO 8601 format)
- `uploaded_by` (object) - User who uploaded the dataset
- `total_records` (integer) - Number of equipment records in dataset
- `avg_flowrate` (float) - Average flowrate across all records (L/min)
- `avg_pressure` (float) - Average pressure across all records (bar)
- `avg_temperature` (float) - Average temperature across all records (°C)
- `type_distribution` (object) - Count of equipment by type

**Example:**
```json
{
  "id": 1,
  "name": "equipment_data.csv",
  "uploaded_at": "2025-11-22T10:30:00Z",
  "uploaded_by": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  },
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

---

### Equipment Record

Represents a single equipment entry from a CSV file.

**Fields:**
- `id` (integer) - Unique identifier
- `equipment_name` (string) - Name of the equipment
- `equipment_type` (string) - Type/category of equipment
- `flowrate` (float) - Flow rate in L/min
- `pressure` (float) - Pressure in bar
- `temperature` (float) - Temperature in °C

**Example:**
```json
{
  "id": 1,
  "equipment_name": "Pump-A1",
  "equipment_type": "Pump",
  "flowrate": 150.5,
  "pressure": 45.2,
  "temperature": 85.0
}
```

---

### User

Represents an authenticated user of the system.

**Fields:**
- `id` (integer) - Unique identifier
- `username` (string) - Username for authentication
- `email` (string) - Email address (optional)

**Example:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com"
}
```

---

## Error Handling

The API uses standard HTTP status codes to indicate success or failure:

### Success Codes
- `200 OK` - Request succeeded
- `201 Created` - Resource created successfully
- `204 No Content` - Request succeeded with no response body

### Client Error Codes
- `400 Bad Request` - Invalid request data or validation error
- `401 Unauthorized` - Authentication required or invalid credentials
- `403 Forbidden` - Authenticated but not authorized for this resource
- `404 Not Found` - Resource does not exist

### Server Error Codes
- `500 Internal Server Error` - Unexpected server error

### Error Response Format

All error responses follow a consistent format:

```json
{
  "error": "Error type",
  "message": "Detailed error message"
}
```

Or for DRF default errors:

```json
{
  "detail": "Error message"
}
```

---

## Pagination

List endpoints that return multiple items use pagination. The response includes:

- `count` - Total number of items
- `next` - URL to next page (null if last page)
- `previous` - URL to previous page (null if first page)
- `results` - Array of items for current page

**Example Paginated Response:**
```json
{
  "count": 250,
  "next": "http://localhost:8000/api/datasets/1/data/?page=3",
  "previous": "http://localhost:8000/api/datasets/1/data/?page=1",
  "results": [...]
}
```

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default varies by endpoint, max: 1000)

---

## Rate Limiting

Currently, no rate limiting is implemented. For production deployments, consider implementing rate limiting to prevent abuse.

---

## CORS Configuration

For development, CORS is configured to allow requests from:
- `http://localhost:3000` (React development server)
- `http://127.0.0.1:3000`

Credentials (cookies, authorization headers) are allowed.

For production, update `CORS_ALLOWED_ORIGINS` in settings.py to include your production frontend URL.

---

## Testing the API

### Using cURL

All examples in this documentation use cURL. Make sure to:
1. Replace `<your-token-here>` with your actual authentication token
2. Replace `{id}` with actual dataset IDs
3. Adjust file paths for file uploads

### Using the Browsable API

1. Start the Django server: `python manage.py runserver`
2. Navigate to `http://localhost:8000/api/` in your browser
3. Log in using the login form
4. Browse and test endpoints interactively

### Using Postman or Similar Tools

1. Create a new request
2. Set the method (GET, POST, DELETE)
3. Set the URL (e.g., `http://localhost:8000/api/datasets/`)
4. Add header: `Authorization: Token <your-token>`
5. For POST requests, set the body (JSON or form-data)
6. Send the request

---

## Sample Data

A sample CSV file is included in the repository at `backend/sample_equipment_data.csv`. This file contains valid equipment data for testing purposes.

**Sample CSV Contents:**
```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A1,Pump,150.5,45.2,85.0
Pump-A2,Pump,145.0,42.8,82.5
Reactor-B1,Reactor,200.0,120.5,350.0
Reactor-B2,Reactor,195.5,118.2,345.0
Heat-Exchanger-C1,Heat Exchanger,180.3,30.0,150.5
Heat-Exchanger-C2,Heat Exchanger,175.8,28.5,148.0
Compressor-D1,Compressor,220.0,85.0,95.0
Compressor-D2,Compressor,215.5,82.5,92.5
Mixer-E1,Mixer,160.0,35.0,75.0
Separator-F1,Separator,185.0,55.0,125.0
```

---

## Requirements Coverage

This API documentation covers the following requirements:

- **1.1** - CSV file upload endpoint with validation
- **2.4** - Summary statistics retrieval (web frontend)
- **4.3** - Dataset history listing (web frontend)
- **5.1** - PDF report generation endpoint

For complete requirements coverage, see the requirements document at `.kiro/specs/chemical-equipment-analytics/requirements.md`.

---

## Additional Resources

- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [Django Documentation](https://docs.djangoproject.com/)
- [Project README](../README.md)
- [Requirements Document](../.kiro/specs/chemical-equipment-analytics/requirements.md)
- [Design Document](../.kiro/specs/chemical-equipment-analytics/design.md)
