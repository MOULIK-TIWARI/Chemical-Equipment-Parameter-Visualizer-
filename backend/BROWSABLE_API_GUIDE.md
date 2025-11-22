# Django REST Framework Browsable API Guide

## Quick Start

The Django REST Framework provides an interactive, web-based interface for exploring and testing the Chemical Equipment Analytics API.

### Accessing the Browsable API

1. **Start the Django development server:**
   ```bash
   cd backend
   python manage.py runserver
   ```

2. **Open your web browser and navigate to:**
   ```
   http://localhost:8000/api/
   ```

3. **You'll see the API root with links to all available endpoints**

## Features

### 1. Interactive Documentation
- View detailed endpoint descriptions
- See request/response formats
- Understand authentication requirements
- Read usage examples

### 2. Test Endpoints Directly
- Fill out forms to make API calls
- Upload files through the browser
- View formatted JSON responses
- Test different HTTP methods (GET, POST, DELETE)

### 3. Authentication
- Login via web interface
- Session authentication for browsing
- Test authenticated endpoints
- View your user information

### 4. Explore API Structure
- Navigate between related resources
- Follow hyperlinks to related endpoints
- Discover available actions
- View OPTIONS metadata

## Step-by-Step Usage

### Step 1: Create a User Account

1. Navigate to: `http://localhost:8000/api/auth/register/`
2. You'll see a form with fields for username, password, and email
3. Fill in the form:
   - Username: `testuser`
   - Password: `testpass123`
   - Email: `test@example.com` (optional)
4. Click the **POST** button
5. You'll receive a response with your authentication token

### Step 2: Login

1. Navigate to: `http://localhost:8000/api/auth/login/`
2. Fill in the login form:
   - Username: `testuser`
   - Password: `testpass123`
3. Click the **POST** button
4. You'll receive your authentication token
5. The browsable API will now show you as logged in

### Step 3: Upload a CSV File

1. Navigate to: `http://localhost:8000/api/datasets/upload/`
2. You'll see a file upload form
3. Click **Choose File** and select a CSV file (or use `sample_equipment_data.csv`)
4. Click the **POST** button
5. View the response with your dataset summary

### Step 4: View Your Datasets

1. Navigate to: `http://localhost:8000/api/datasets/`
2. You'll see a list of your uploaded datasets (last 5)
3. Each dataset shows:
   - ID, name, upload timestamp
   - Total records
   - Average values
   - Type distribution

### Step 5: View Dataset Details

1. From the dataset list, click on a dataset ID link
2. Or navigate to: `http://localhost:8000/api/datasets/1/`
3. You'll see complete dataset information including all equipment records

### Step 6: Get Summary Statistics

1. Navigate to: `http://localhost:8000/api/datasets/1/summary/`
2. View just the summary statistics without all records
3. Useful for dashboard displays

### Step 7: Download PDF Report

1. Navigate to: `http://localhost:8000/api/datasets/1/report/`
2. The PDF will download automatically
3. Open the PDF to view the formatted report with charts

### Step 8: View Paginated Data

1. Navigate to: `http://localhost:8000/api/datasets/1/data/`
2. View equipment records with pagination
3. Use query parameters:
   - `?page=2` - Get page 2
   - `?page_size=100` - Get 100 records per page
4. Click **next** and **previous** links to navigate

## Understanding the Interface

### Top Navigation Bar
- **GET/POST/DELETE buttons**: Select HTTP method
- **Media type dropdown**: Choose response format (JSON/HTML)
- **Filters button**: Apply query filters (if available)

### Main Content Area
- **Endpoint description**: Detailed documentation from docstrings
- **Request form**: Fill out to make API calls
- **Response section**: View formatted responses

### Bottom Section
- **OPTIONS**: View endpoint metadata
- **Raw data**: See JSON response
- **HTML form**: Interactive form for testing

## Tips and Tricks

### 1. Using Session Authentication
Once you login via the browsable API, you're authenticated for all subsequent requests in that browser session. No need to include tokens manually.

### 2. Viewing Raw JSON
Click the **GET** button without any parameters to see the raw JSON response. This is what programmatic clients (React, PyQt5) will receive.

### 3. Testing Error Scenarios
Try invalid inputs to see error responses:
- Upload a non-CSV file
- Provide invalid credentials
- Access a dataset that doesn't exist

### 4. OPTIONS Requests
Click the **OPTIONS** button to see:
- Available HTTP methods
- Required/optional fields
- Field types and constraints
- Endpoint description

### 5. Copying cURL Commands
The browsable API shows equivalent cURL commands. Copy these for:
- Command-line testing
- Documentation examples
- Automation scripts

## Common Workflows

### Workflow 1: Upload and Analyze Data
1. Login: `POST /api/auth/login/`
2. Upload CSV: `POST /api/datasets/upload/`
3. View summary: `GET /api/datasets/{id}/summary/`
4. Download report: `GET /api/datasets/{id}/report/`

### Workflow 2: Browse Historical Data
1. Login: `POST /api/auth/login/`
2. List datasets: `GET /api/datasets/`
3. Select dataset: `GET /api/datasets/{id}/`
4. View records: `GET /api/datasets/{id}/data/`

### Workflow 3: Test Authentication
1. Register: `POST /api/auth/register/`
2. Login: `POST /api/auth/login/`
3. Access protected endpoint: `GET /api/datasets/`
4. Logout: `POST /api/auth/logout/`

## Troubleshooting

### Issue: "Authentication credentials were not provided"
**Solution:** Login via the browsable API or include token in Authorization header

### Issue: "You do not have permission to perform this action"
**Solution:** Ensure you're logged in as the dataset owner

### Issue: "Not found"
**Solution:** Check the dataset ID exists and belongs to you

### Issue: CSV upload fails
**Solution:** 
- Verify file has .csv extension
- Check required columns are present
- Ensure numeric fields contain valid numbers

## Advanced Features

### 1. Filtering (if implemented)
Add query parameters to filter results:
```
/api/datasets/?name=equipment_data
```

### 2. Ordering (if implemented)
Sort results by field:
```
/api/datasets/?ordering=-uploaded_at
```

### 3. Search (if implemented)
Search across fields:
```
/api/datasets/?search=pump
```

## Comparison: Browsable API vs. Programmatic Access

### Browsable API (Browser)
- ✅ Interactive forms
- ✅ Visual feedback
- ✅ Session authentication
- ✅ Easy exploration
- ❌ Not for automation

### Programmatic Access (cURL/Axios/Requests)
- ✅ Automation-friendly
- ✅ Token authentication
- ✅ Scriptable
- ✅ Integration with apps
- ❌ Less visual

## Security Notes

### Development vs. Production

**Development (Current Setup):**
- Browsable API enabled
- Debug mode on
- CORS allows localhost
- Session authentication available

**Production (Recommended):**
- Consider disabling browsable API
- Debug mode off
- CORS restricted to production domains
- Token authentication only
- HTTPS required

### Best Practices
1. Don't share authentication tokens
2. Use HTTPS in production
3. Implement rate limiting
4. Validate all inputs
5. Log security events

## Additional Resources

- **API Documentation**: `backend/API_DOCUMENTATION.md`
- **Django REST Framework Docs**: https://www.django-rest-framework.org/
- **Sample CSV File**: `backend/sample_equipment_data.csv`
- **Requirements**: `.kiro/specs/chemical-equipment-analytics/requirements.md`

## Support

For issues or questions:
1. Check the API documentation
2. Review Django REST Framework docs
3. Examine server logs for errors
4. Test with cURL to isolate issues

---

**Happy API Exploring! 🚀**
