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
    """Custom pagination class for equipment records."""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000


class LoginView(APIView):
    """Handle user login and token generation."""
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.id,
                'username': user.username
            })
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class RegisterView(APIView):
    """Handle user registration."""
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')
        
        if not username or not password:
            return Response(
                {'error': 'Username and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Username already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = User.objects.create_user(username=username, password=password, email=email)
        token = Token.objects.create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    """Handle user logout."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({'message': 'Successfully logged out'})


class DatasetViewSet(viewsets.ModelViewSet):
    """ViewSet for managing datasets."""
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
        Handle CSV file upload.
        
        This endpoint:
        1. Receives a CSV file via multipart/form-data
        2. Validates the file is CSV format
        3. Uses CSVProcessor to parse and validate the file
        4. Creates Dataset and EquipmentRecord instances
        5. Calculates summary statistics
        6. Maintains history limit (last 5 datasets)
        
        Requirements: 1.1, 1.2, 1.3, 1.4
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
        Return all equipment records for a specific dataset with pagination.
        
        This endpoint:
        1. Retrieves the dataset by ID
        2. Checks that the user owns the dataset (via IsDatasetOwner permission)
        3. Returns paginated equipment records
        
        Query parameters:
        - page: Page number (default: 1)
        - page_size: Number of records per page (default: 50, max: 1000)
        
        Requirements: 4.5
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
        Return calculated summary statistics for a specific dataset.
        
        This endpoint:
        1. Retrieves the dataset by ID
        2. Checks that the user owns the dataset (via IsDatasetOwner permission)
        3. Returns summary statistics including:
           - Total record count
           - Average flowrate, pressure, and temperature
           - Equipment type distribution
        
        Requirements: 2.4, 2.5
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
        Generate and return a PDF report for a specific dataset.
        
        This endpoint:
        1. Retrieves the dataset by ID
        2. Checks that the user owns the dataset (via IsDatasetOwner permission)
        3. Generates a PDF report using PDFGenerator service
        4. Returns the PDF file as a downloadable response
        
        The PDF report includes:
        - Dataset information (name, ID, upload timestamp)
        - Summary statistics (total count, averages)
        - Equipment type distribution chart
        - Table of equipment records
        
        Requirements: 5.1, 5.2, 5.4
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
