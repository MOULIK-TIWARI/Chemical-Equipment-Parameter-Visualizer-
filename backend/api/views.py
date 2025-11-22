"""
API Views for Chemical Equipment Analytics.

This module provides all API endpoints for the application including:
- Authentication (login, register, logout)
- Dataset management (upload, retrieve, list, delete)
- Equipment record retrieval
- Summary statistics
- PDF report generation

Requirements: 1.1, 1.2, 1.3, 1.4, 2.4, 2.5, 4.3, 4.4, 4.5, 5.1, 5.2, 5.4, 6.1, 6.2, 6.3, 6.4, 6.5
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from .models import Dataset, EquipmentRecord
from .serializers import DatasetSerializer, DatasetDetailSerializer, EquipmentRecordSerializer
from .permissions import IsDatasetOwner
from .services.csv_processor import CSVProcessor, CSVValidationError
from .services.pdf_generator import PDFGenerator


class EquipmentRecordPagination(PageNumberPagination):
    """
    Custom pagination class for equipment records.
    
    Provides configurable pagination with:
    - Default page size of 50 records
    - Client-configurable page size via query parameter
    - Maximum page size limit of 1000 records
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000


class LoginView(APIView):
    """
    User Authentication - Login
    
    Authenticate a user and receive an authentication token for subsequent API requests.
    
    ## Endpoint
    `POST /api/auth/login/`
    
    ## Authentication Required
    No
    
    ## Request Format
    ```json
    {
        "username": "string",
        "password": "string"
    }
    ```
    
    ## Success Response (200 OK)
    ```json
    {
        "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
        "user_id": 1,
        "username": "john_doe"
    }
    ```
    
    ## Error Response (401 Unauthorized)
    ```json
    {
        "error": "Invalid credentials"
    }
    ```
    
    ## Usage
    Include the returned token in subsequent requests:
    ```
    Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
    ```
    
    **Requirements:** 6.2, 6.4
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Authenticate user and return authentication token.
        
        Args:
            request: HTTP request containing username and password
            
        Returns:
            Response with token and user info on success,
            or error message on failure
        """
        username = request.data.get('username')
        password = request.data.get('password')
        
        # Authenticate user with Django's authentication system
        user = authenticate(username=username, password=password)
        if user:
            # Get or create authentication token for the user
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.id,
                'username': user.username
            })
        
        # Return error if authentication fails
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class RegisterView(APIView):
    """
    User Registration
    
    Register a new user account and receive an authentication token.
    
    ## Endpoint
    `POST /api/auth/register/`
    
    ## Authentication Required
    No
    
    ## Request Format
    ```json
    {
        "username": "string",
        "password": "string",
        "email": "string (optional)"
    }
    ```
    
    ## Success Response (201 Created)
    ```json
    {
        "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
        "user_id": 1,
        "username": "john_doe"
    }
    ```
    
    ## Error Responses
    
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
    
    **Requirements:** 6.2
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Register a new user account.
        
        Args:
            request: HTTP request containing username, password, and optional email
            
        Returns:
            Response with token and user info on success,
            or error message on failure
        """
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')
        
        # Validate required fields
        if not username or not password:
            return Response(
                {'error': 'Username and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Username already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create new user
        user = User.objects.create_user(username=username, password=password, email=email)
        
        # Create authentication token for the new user
        token = Token.objects.create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    """
    User Logout
    
    Logout the current user by deleting their authentication token.
    
    ## Endpoint
    `POST /api/auth/logout/`
    
    ## Authentication Required
    Yes - Include token in Authorization header
    
    ## Request Format
    No request body required.
    
    ## Success Response (200 OK)
    ```json
    {
        "message": "Successfully logged out"
    }
    ```
    
    ## Notes
    After logout, the authentication token will be deleted and can no longer be used.
    The user must login again to receive a new token.
    
    **Requirements:** 6.5
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Logout user by deleting their authentication token.
        
        Args:
            request: HTTP request with authentication token
            
        Returns:
            Response with success message
        """
        # Delete the user's authentication token
        request.user.auth_token.delete()
        return Response({'message': 'Successfully logged out'})


class DatasetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing datasets.
    
    Provides CRUD operations for datasets with the following endpoints:
    - GET /api/datasets/ - List last 5 datasets
    - POST /api/datasets/upload/ - Upload new CSV file
    - GET /api/datasets/{id}/ - Retrieve specific dataset
    - GET /api/datasets/{id}/data/ - Get equipment records (paginated)
    - GET /api/datasets/{id}/summary/ - Get summary statistics
    - GET /api/datasets/{id}/report/ - Generate PDF report
    - DELETE /api/datasets/{id}/ - Delete dataset
    
    All endpoints require authentication.
    Users can only access their own datasets.
    
    Requirements: 1.1, 1.2, 1.3, 1.4, 2.4, 2.5, 4.3, 4.4, 4.5, 5.1, 5.2, 5.4
    """
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    permission_classes = [IsAuthenticated, IsDatasetOwner]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """
        Return datasets for the authenticated user.
        For list action, return only the last 5 datasets.
        For other actions, return all user's datasets (for permission checking).
        """
        user_datasets = Dataset.objects.filter(uploaded_by=self.request.user).order_by('-uploaded_at')
        
        if self.action == 'list':
            # Return only the last 5 datasets for list view
            return user_datasets[:5]
        
        # For retrieve, update, destroy - return all user datasets
        return user_datasets

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DatasetDetailSerializer
        return DatasetSerializer
    
    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        if self.action in ['list', 'create', 'upload']:
            # List, create, and upload only require authentication
            permission_classes = [IsAuthenticated]
        else:
            # Retrieve, update, partial_update, destroy require ownership
            permission_classes = [IsAuthenticated, IsDatasetOwner]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['post'], url_path='upload')
    def upload(self, request):
        """
        Upload CSV File
        
        Upload a CSV file containing chemical equipment data.
        
        ## Endpoint
        `POST /api/datasets/upload/`
        
        ## Authentication Required
        Yes
        
        ## Content Type
        `multipart/form-data`
        
        ## Request Parameters
        - `file`: CSV file (required)
        
        ## CSV File Format
        The CSV must contain these columns:
        - Equipment Name (string)
        - Type (string)
        - Flowrate (positive float, L/min)
        - Pressure (positive float, bar)
        - Temperature (float, °C)
        
        ## Processing Steps
        1. Validates file is CSV format
        2. Parses and validates CSV structure
        3. Creates Dataset and EquipmentRecord instances
        4. Calculates summary statistics
        5. Maintains history limit (last 5 datasets per user)
        
        ## Success Response (201 Created)
        Returns the created dataset with summary statistics.
        
        ## Error Responses
        - **400 Bad Request**: No file provided, invalid format, or validation failed
        - **500 Internal Server Error**: Unexpected processing error
        
        **Requirements:** 1.1, 1.2, 1.3, 1.4
        """
        # Check if file is present in request
        if 'file' not in request.FILES:
            return Response(
                {
                    'error': 'No file provided',
                    'message': 'Please upload a CSV file using the "file" field'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_file = request.FILES['file']
        
        # Validate file is CSV format
        if not uploaded_file.name.endswith('.csv'):
            return Response(
                {
                    'error': 'Invalid file format',
                    'message': 'Only CSV files are accepted. Please upload a file with .csv extension'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Initialize CSV processor
        csv_processor = CSVProcessor()
        
        try:
            # Parse and validate CSV file
            # CSVProcessor will validate structure, required columns, and data types
            df, records_data = csv_processor.parse_csv_file(uploaded_file)
            
            # Create Dataset instance (not yet saved)
            dataset = Dataset(
                name=uploaded_file.name,
                uploaded_by=request.user,
                total_records=len(records_data)
            )
            
            # Save dataset to get an ID for foreign key relationships
            dataset.save()
            
            # Create equipment records using CSVProcessor
            csv_processor.create_equipment_records(dataset, records_data)
            
            # Calculate and save summary statistics
            dataset.calculate_summary_statistics()
            dataset.save()
            
            # Maintain history limit (keep only last 5 datasets per user)
            Dataset.maintain_history_limit(request.user, limit=5)
            
            # Serialize and return the created dataset
            serializer = DatasetSerializer(dataset)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
            
        except CSVValidationError as e:
            # Handle CSV validation errors
            return Response(
                {
                    'error': 'CSV validation failed',
                    'message': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Handle unexpected errors
            return Response(
                {
                    'error': 'Upload failed',
                    'message': f'An error occurred while processing the file: {str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'], url_path='data')
    def data(self, request, pk=None):
        """
        Get Equipment Records (Paginated)
        
        Retrieve all equipment records for a specific dataset with pagination.
        
        ## Endpoint
        `GET /api/datasets/{id}/data/`
        
        ## Authentication Required
        Yes - Must be dataset owner
        
        ## URL Parameters
        - `id`: Dataset ID (integer)
        
        ## Query Parameters
        - `page`: Page number (default: 1)
        - `page_size`: Records per page (default: 50, max: 1000)
        
        ## Success Response (200 OK)
        Returns paginated equipment records with count, next/previous links.
        
        ## Use Case
        Use this endpoint instead of the detail endpoint for large datasets
        to avoid loading all records at once.
        
        **Requirements:** 4.5
        """
        dataset = self.get_object()
        
        # Get all equipment records for this dataset
        equipment_records = EquipmentRecord.objects.filter(dataset=dataset).order_by('id')
        
        # Apply pagination
        paginator = EquipmentRecordPagination()
        paginated_records = paginator.paginate_queryset(equipment_records, request)
        
        # Serialize the paginated records
        serializer = EquipmentRecordSerializer(paginated_records, many=True)
        
        # Return paginated response
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['get'], url_path='summary')
    def summary(self, request, pk=None):
        """
        Get Summary Statistics
        
        Retrieve calculated summary statistics for a specific dataset.
        
        ## Endpoint
        `GET /api/datasets/{id}/summary/`
        
        ## Authentication Required
        Yes - Must be dataset owner
        
        ## URL Parameters
        - `id`: Dataset ID (integer)
        
        ## Success Response (200 OK)
        Returns summary statistics including:
        - Total record count
        - Average flowrate (L/min)
        - Average pressure (bar)
        - Average temperature (°C)
        - Equipment type distribution (count by type)
        
        ## Use Case
        Use this endpoint to get just the summary data without
        loading all equipment records.
        
        **Requirements:** 2.4, 2.5
        """
        dataset = self.get_object()
        
        # Return the summary statistics
        return Response({
            'id': dataset.id,
            'name': dataset.name,
            'uploaded_at': dataset.uploaded_at,
            'total_records': dataset.total_records,
            'avg_flowrate': dataset.avg_flowrate,
            'avg_pressure': dataset.avg_pressure,
            'avg_temperature': dataset.avg_temperature,
            'type_distribution': dataset.type_distribution
        })

    @action(detail=True, methods=['get'], url_path='report')
    def report(self, request, pk=None):
        """
        Generate PDF Report
        
        Generate and download a PDF report for a specific dataset.
        
        ## Endpoint
        `GET /api/datasets/{id}/report/`
        
        ## Authentication Required
        Yes - Must be dataset owner
        
        ## URL Parameters
        - `id`: Dataset ID (integer)
        
        ## Success Response (200 OK)
        - Content-Type: `application/pdf`
        - Content-Disposition: `attachment; filename="equipment_report_{id}_{name}"`
        - Body: PDF file binary data
        
        ## PDF Report Contents
        - Dataset information (name, ID, upload timestamp)
        - Summary statistics (total count, averages)
        - Equipment type distribution chart (bar chart)
        - Table of equipment records (first 100 records)
        
        ## Error Response
        - **500 Internal Server Error**: PDF generation failed
        
        ## Usage
        Download the PDF file directly or open in browser.
        The file will be named based on the dataset ID and name.
        
        **Requirements:** 5.1, 5.2, 5.4
        """
        dataset = self.get_object()
        
        try:
            # Initialize PDF generator
            pdf_generator = PDFGenerator()
            
            # Generate the PDF report
            pdf_buffer = pdf_generator.generate_dataset_report(
                dataset=dataset,
                include_records=True,
                max_records=100  # Limit to first 100 records to keep PDF size reasonable
            )
            
            # Create HTTP response with PDF content
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            
            # Set Content-Disposition header to suggest filename for download
            filename = f"equipment_report_{dataset.id}_{dataset.name}"
            # Sanitize filename - remove or replace problematic characters
            filename = filename.replace(' ', '_').replace(',', '_')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            # Handle PDF generation errors
            return Response(
                {
                    'error': 'PDF generation failed',
                    'message': f'An error occurred while generating the report: {str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
