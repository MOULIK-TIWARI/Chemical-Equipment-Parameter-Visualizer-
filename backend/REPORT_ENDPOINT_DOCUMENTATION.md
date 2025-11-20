# PDF Report Endpoint Documentation

## Overview

The PDF Report endpoint generates and downloads a comprehensive PDF report for a specific dataset. This endpoint is part of the Chemical Equipment Analytics API.

## Endpoint Details

**URL:** `/api/datasets/{id}/report/`

**Method:** `GET`

**Authentication:** Required (Token Authentication)

**Permissions:** User must own the dataset (IsDatasetOwner)

## URL Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | The unique identifier of the dataset |

## Request Headers

| Header | Value | Required | Description |
|--------|-------|----------|-------------|
| Authorization | Token {token} | Yes | Authentication token obtained from login |

## Response

### Success Response (200 OK)

**Content-Type:** `application/pdf`

**Headers:**
- `Content-Disposition: attachment; filename="equipment_report_{id}_{dataset_name}"`

**Body:** Binary PDF file content

### Error Responses

#### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

#### 404 Not Found
```json
{
  "detail": "Not found."
}
```

#### 500 Internal Server Error
```json
{
  "error": "PDF generation failed",
  "message": "An error occurred while generating the report: {error_details}"
}
```

## PDF Report Contents

The generated PDF report includes the following sections:

### 1. Report Title
- "Chemical Equipment Analytics Report"

### 2. Dataset Information
- Dataset ID
- Dataset Name
- Upload Timestamp
- Uploaded By (username)

### 3. Summary Statistics
- Total Equipment Records
- Average Flowrate (L/min)
- Average Pressure (bar)
- Average Temperature (°C)

### 4. Equipment Type Distribution
- Bar chart visualization showing count by equipment type
- Table with equipment type, count, and percentage

### 5. Equipment Records Table
- Equipment Name
- Type
- Flowrate (L/min)
- Pressure (bar)
- Temperature (°C)
- Limited to first 100 records to keep PDF size reasonable

### 6. Footer
- Report generation timestamp

## Example Usage

### cURL

```bash
curl -X GET \
  http://localhost:8000/api/datasets/1/report/ \
  -H 'Authorization: Token your_auth_token_here' \
  --output equipment_report.pdf
```

### Python (requests)

```python
import requests

url = "http://localhost:8000/api/datasets/1/report/"
headers = {
    "Authorization": "Token your_auth_token_here"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    with open("equipment_report.pdf", "wb") as f:
        f.write(response.content)
    print("PDF downloaded successfully!")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

### JavaScript (fetch)

```javascript
const datasetId = 1;
const token = 'your_auth_token_here';

fetch(`http://localhost:8000/api/datasets/${datasetId}/report/`, {
  method: 'GET',
  headers: {
    'Authorization': `Token ${token}`
  }
})
  .then(response => {
    if (response.ok) {
      return response.blob();
    }
    throw new Error('Network response was not ok');
  })
  .then(blob => {
    // Create a download link
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `equipment_report_${datasetId}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  })
  .catch(error => {
    console.error('Error downloading PDF:', error);
  });
```

### PyQt5 (Desktop Application)

```python
import requests
from PyQt5.QtWidgets import QFileDialog, QMessageBox

def download_report(dataset_id, auth_token):
    """Download PDF report for a dataset."""
    url = f"http://localhost:8000/api/datasets/{dataset_id}/report/"
    headers = {"Authorization": f"Token {auth_token}"}
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            # Open file dialog to save PDF
            filename, _ = QFileDialog.getSaveFileName(
                None,
                "Save PDF Report",
                f"equipment_report_{dataset_id}.pdf",
                "PDF Files (*.pdf)"
            )
            
            if filename:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                QMessageBox.information(
                    None,
                    "Success",
                    f"Report saved to {filename}"
                )
        else:
            QMessageBox.warning(
                None,
                "Error",
                f"Failed to download report: {response.status_code}"
            )
    except Exception as e:
        QMessageBox.critical(
            None,
            "Error",
            f"An error occurred: {str(e)}"
        )
```

## Implementation Details

### Service Layer

The endpoint uses the `PDFGenerator` service class to generate the PDF report:

```python
from .services.pdf_generator import PDFGenerator

pdf_generator = PDFGenerator()
pdf_buffer = pdf_generator.generate_dataset_report(
    dataset=dataset,
    include_records=True,
    max_records=100
)
```

### PDF Generation Features

- **ReportLab**: Used for PDF document creation
- **Matplotlib**: Used for chart generation (embedded as images)
- **Custom Styling**: Professional formatting with custom fonts and colors
- **Pagination**: Automatic page breaks for large datasets
- **Charts**: Bar chart for equipment type distribution

### Performance Considerations

- Records are limited to 100 to keep PDF size reasonable
- Charts are generated in-memory using matplotlib's Agg backend
- PDF is generated on-demand (not cached)
- Generation typically takes 1-3 seconds depending on dataset size

## Requirements Validation

This endpoint satisfies the following requirements:

- **Requirement 5.1**: Generate PDF document containing dataset summary statistics
- **Requirement 5.2**: Support PDF generation from both web and desktop frontends
- **Requirement 5.4**: Provide PDF file for download to the user

## Testing

The endpoint has been tested with:

1. ✓ Authentication validation (401 for unauthenticated requests)
2. ✓ Permission validation (403/404 for unauthorized access)
3. ✓ Successful PDF generation (200 with valid PDF content)
4. ✓ Non-existent dataset handling (404)
5. ✓ PDF content validation (valid PDF signature)
6. ✓ Content-Type and Content-Disposition headers
7. ✓ URL routing and reverse lookup

## Related Endpoints

- `GET /api/datasets/` - List all datasets
- `GET /api/datasets/{id}/` - Get dataset details
- `GET /api/datasets/{id}/data/` - Get equipment records
- `GET /api/datasets/{id}/summary/` - Get summary statistics
- `POST /api/datasets/upload/` - Upload new dataset

## Notes

- The PDF filename is automatically sanitized to remove problematic characters
- The report includes a timestamp of when it was generated
- Charts are embedded as PNG images at 150 DPI for good quality
- The PDF uses letter-size pages with standard margins
