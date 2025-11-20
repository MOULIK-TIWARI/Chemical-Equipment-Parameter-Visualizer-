# Dataset Data Endpoint Usage

## Endpoint: GET /api/datasets/{id}/data/

This endpoint returns all equipment records for a specific dataset with pagination support.

### Authentication
Requires authentication token in the header:
```
Authorization: Token <your-token-here>
```

### URL Parameters
- `id` (required): The dataset ID

### Query Parameters
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Number of records per page (default: 50, max: 1000)

### Response Format
```json
{
  "count": 100,
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
    // ... more records
  ]
}
```

### Example Usage

#### Get first page (default 50 records per page)
```bash
curl -H "Authorization: Token your-token-here" \
  http://localhost:8000/api/datasets/1/data/
```

#### Get specific page
```bash
curl -H "Authorization: Token your-token-here" \
  http://localhost:8000/api/datasets/1/data/?page=2
```

#### Custom page size
```bash
curl -H "Authorization: Token your-token-here" \
  http://localhost:8000/api/datasets/1/data/?page_size=100
```

### Error Responses

#### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### Features
- ✅ Pagination support for large datasets
- ✅ Customizable page size (up to 1000 records)
- ✅ User isolation (users can only access their own datasets)
- ✅ Ordered by record ID for consistent pagination
- ✅ Returns all equipment record fields

### Requirements Satisfied
- **Requirement 4.5**: Users can select and view historical datasets with full data

---

## Endpoint: GET /api/datasets/{id}/summary/

This endpoint returns calculated summary statistics for a specific dataset, including averages and type distribution.

### Authentication
Requires authentication token in the header:
```
Authorization: Token <your-token-here>
```

### URL Parameters
- `id` (required): The dataset ID

### Response Format
```json
{
  "id": 1,
  "name": "test_equipment_data.csv",
  "uploaded_at": "2025-11-20T10:30:00Z",
  "total_records": 25,
  "avg_flowrate": 172.7,
  "avg_pressure": 61.425,
  "avg_temperature": 168.875,
  "type_distribution": {
    "Pump": 8,
    "Reactor": 6,
    "Heat Exchanger": 7,
    "Compressor": 4
  }
}
```

### Example Usage

#### Get summary statistics for a dataset
```bash
curl -H "Authorization: Token your-token-here" \
  http://localhost:8000/api/datasets/1/summary/
```

### Error Responses

#### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### Features
- ✅ Returns total record count
- ✅ Calculates average flowrate, pressure, and temperature
- ✅ Provides equipment type distribution
- ✅ User isolation (users can only access their own datasets)
- ✅ Handles empty datasets gracefully (returns null for averages)

### Requirements Satisfied
- **Requirement 2.4**: Web Frontend can request summary statistics from Backend API
- **Requirement 2.5**: Desktop Frontend can request summary statistics from Backend API
