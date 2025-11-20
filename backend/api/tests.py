from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Dataset, EquipmentRecord
from .services.csv_processor import CSVProcessor, CSVValidationError
from .services.analytics_service import AnalyticsService
import io


class AuthenticationPermissionTests(APITestCase):
    """Test authentication and permission functionality."""
    
    def setUp(self):
        """Set up test users and authentication tokens."""
        self.user1 = User.objects.create_user(username='testuser1', password='testpass123')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass123')
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)
        self.client = APIClient()
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated requests are denied."""
        response = self.client.get('/api/datasets/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_access_allowed(self):
        """Test that authenticated requests are allowed."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        response = self.client.get('/api/datasets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_invalid_token_denied(self):
        """Test that invalid tokens are rejected."""
        self.client.credentials(HTTP_AUTHORIZATION='Token invalid_token_12345')
        response = self.client.get('/api/datasets/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_dataset_owner_access(self):
        """Test that users can only access their own datasets."""
        # Create a dataset for user1
        dataset = Dataset.objects.create(
            name='test_dataset.csv',
            uploaded_by=self.user1,
            total_records=10,
            avg_flowrate=100.0,
            avg_pressure=50.0,
            avg_temperature=75.0,
            type_distribution={'Pump': 5, 'Reactor': 5}
        )
        
        # User1 should be able to access their own dataset
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        response = self.client.get(f'/api/datasets/{dataset.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # User2 should not be able to access user1's dataset
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)
        response = self.client.get(f'/api/datasets/{dataset.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CSVProcessorTests(TestCase):
    """Test CSV processing functionality."""
    
    def setUp(self):
        """Set up test data and CSV processor."""
        self.processor = CSVProcessor()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
        # Valid CSV content
        self.valid_csv = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A1,Pump,150.5,45.2,85.0
Reactor-B2,Reactor,200.0,120.5,350.0
Heat-Exchanger-C3,Heat Exchanger,180.3,30.0,150.5"""
    
    def test_parse_csv_file_success(self):
        """Test successful CSV parsing."""
        csv_file = io.StringIO(self.valid_csv)
        
        df, records = self.processor.parse_csv_file(csv_file)
        
        # Check DataFrame
        self.assertEqual(len(df), 3)
        self.assertIn('Equipment Name', df.columns)
        
        # Check parsed records
        self.assertEqual(len(records), 3)
        self.assertEqual(records[0]['equipment_name'], 'Pump-A1')
        self.assertEqual(records[0]['equipment_type'], 'Pump')
        self.assertEqual(records[0]['flowrate'], 150.5)
        self.assertEqual(records[0]['pressure'], 45.2)
        self.assertEqual(records[0]['temperature'], 85.0)
    
    def test_parse_csv_file_missing_columns(self):
        """Test CSV parsing with missing columns."""
        invalid_csv = """Equipment Name,Type,Flowrate
Pump-A1,Pump,150.5"""
        
        csv_file = io.StringIO(invalid_csv)
        
        with self.assertRaises(CSVValidationError) as context:
            self.processor.parse_csv_file(csv_file)
        
        self.assertIn('Missing required columns', str(context.exception))
    
    def test_parse_csv_file_invalid_numeric(self):
        """Test CSV parsing with invalid numeric values."""
        invalid_csv = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A1,Pump,invalid,45.2,85.0"""
        
        csv_file = io.StringIO(invalid_csv)
        
        with self.assertRaises(CSVValidationError) as context:
            self.processor.parse_csv_file(csv_file)
        
        self.assertIn('non-numeric', str(context.exception))
    
    def test_create_equipment_records(self):
        """Test creating equipment record model instances."""
        # Create a dataset
        dataset = Dataset.objects.create(
            name='test_dataset.csv',
            uploaded_by=self.user,
            total_records=0
        )
        
        # Parse CSV
        csv_file = io.StringIO(self.valid_csv)
        df, records_data = self.processor.parse_csv_file(csv_file)
        
        # Create equipment records
        created_records = self.processor.create_equipment_records(dataset, records_data)
        
        # Verify records were created
        self.assertEqual(len(created_records), 3)
        self.assertEqual(EquipmentRecord.objects.filter(dataset=dataset).count(), 3)
        
        # Verify first record
        first_record = EquipmentRecord.objects.filter(dataset=dataset).first()
        self.assertEqual(first_record.equipment_name, 'Pump-A1')
        self.assertEqual(first_record.equipment_type, 'Pump')
        self.assertEqual(first_record.flowrate, 150.5)
    
    def test_parse_csv_file_empty(self):
        """Test CSV parsing with empty file."""
        empty_csv = ""
        csv_file = io.StringIO(empty_csv)
        
        with self.assertRaises(CSVValidationError) as context:
            self.processor.parse_csv_file(csv_file)
        
        self.assertIn('empty', str(context.exception).lower())
    
    def test_validate_negative_flowrate(self):
        """Test validation rejects negative flowrate values."""
        invalid_csv = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A1,Pump,-150.5,45.2,85.0"""
        
        csv_file = io.StringIO(invalid_csv)
        
        with self.assertRaises(CSVValidationError) as context:
            self.processor.parse_csv_file(csv_file)
        
        error_msg = str(context.exception)
        self.assertIn('Flowrate', error_msg)
        self.assertIn('positive', error_msg.lower())
    
    def test_validate_negative_pressure(self):
        """Test validation rejects negative pressure values."""
        invalid_csv = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A1,Pump,150.5,-45.2,85.0"""
        
        csv_file = io.StringIO(invalid_csv)
        
        with self.assertRaises(CSVValidationError) as context:
            self.processor.parse_csv_file(csv_file)
        
        error_msg = str(context.exception)
        self.assertIn('Pressure', error_msg)
        self.assertIn('positive', error_msg.lower())
    
    def test_validate_empty_equipment_name(self):
        """Test validation rejects empty equipment names."""
        invalid_csv = """Equipment Name,Type,Flowrate,Pressure,Temperature
,Pump,150.5,45.2,85.0"""
        
        csv_file = io.StringIO(invalid_csv)
        
        with self.assertRaises(CSVValidationError) as context:
            self.processor.parse_csv_file(csv_file)
        
        error_msg = str(context.exception)
        self.assertIn('Equipment Name', error_msg)
        self.assertIn('empty', error_msg.lower())
    
    def test_validate_empty_type(self):
        """Test validation rejects empty equipment type."""
        invalid_csv = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A1,,150.5,45.2,85.0"""
        
        csv_file = io.StringIO(invalid_csv)
        
        with self.assertRaises(CSVValidationError) as context:
            self.processor.parse_csv_file(csv_file)
        
        error_msg = str(context.exception)
        self.assertIn('Type', error_msg)
        self.assertIn('empty', error_msg.lower())
    
    def test_validate_multiple_errors(self):
        """Test validation reports multiple errors in detailed message."""
        invalid_csv = """Equipment Name,Type,Flowrate,Pressure,Temperature
,Pump,-150.5,45.2,85.0
Reactor-B2,,200.0,-120.5,350.0"""
        
        csv_file = io.StringIO(invalid_csv)
        
        with self.assertRaises(CSVValidationError) as context:
            self.processor.parse_csv_file(csv_file)
        
        error_msg = str(context.exception)
        # Should contain multiple error details
        self.assertIn('empty', error_msg.lower())
        self.assertIn('positive', error_msg.lower())
    
    def test_validate_zero_flowrate_allowed(self):
        """Test that zero flowrate is rejected (must be positive, not non-negative)."""
        csv_with_zero = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A1,Pump,0,45.2,85.0"""
        
        csv_file = io.StringIO(csv_with_zero)
        
        # Zero should be rejected for flowrate (must be positive)
        with self.assertRaises(CSVValidationError) as context:
            self.processor.parse_csv_file(csv_file)
        
        error_msg = str(context.exception)
        self.assertIn('Flowrate', error_msg)
    
    def test_validate_zero_pressure_allowed(self):
        """Test that zero pressure is rejected (must be positive, not non-negative)."""
        csv_with_zero = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A1,Pump,150.5,0,85.0"""
        
        csv_file = io.StringIO(csv_with_zero)
        
        # Zero should be rejected for pressure (must be positive)
        with self.assertRaises(CSVValidationError) as context:
            self.processor.parse_csv_file(csv_file)
        
        error_msg = str(context.exception)
        self.assertIn('Pressure', error_msg)
    
    def test_validate_negative_temperature_allowed(self):
        """Test that negative temperature is allowed (can be negative in Celsius)."""
        csv_with_negative_temp = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A1,Pump,150.5,45.2,-10.0"""
        
        csv_file = io.StringIO(csv_with_negative_temp)
        
        # Should not raise an error - negative temperature is valid
        df, records = self.processor.parse_csv_file(csv_file)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['temperature'], -10.0)


class DatasetUploadTests(APITestCase):
    """Test dataset upload endpoint functionality."""
    
    def setUp(self):
        """Set up test user and authentication."""
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        # Valid CSV content
        self.valid_csv = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A1,Pump,150.5,45.2,85.0
Reactor-B2,Reactor,200.0,120.5,350.0
Heat-Exchanger-C3,Heat Exchanger,180.3,30.0,150.5"""
    
    def test_upload_valid_csv(self):
        """Test successful CSV file upload."""
        csv_file = io.StringIO(self.valid_csv)
        csv_file.name = 'test_equipment.csv'
        
        response = self.client.post(
            '/api/datasets/upload/',
            {'file': csv_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['name'], 'test_equipment.csv')
        self.assertEqual(response.data['total_records'], 3)
        
        # Verify dataset was created
        dataset = Dataset.objects.get(id=response.data['id'])
        self.assertEqual(dataset.uploaded_by, self.user)
        self.assertEqual(dataset.total_records, 3)
        
        # Verify equipment records were created
        self.assertEqual(EquipmentRecord.objects.filter(dataset=dataset).count(), 3)
        
        # Verify summary statistics were calculated
        self.assertIsNotNone(dataset.avg_flowrate)
        self.assertIsNotNone(dataset.avg_pressure)
        self.assertIsNotNone(dataset.avg_temperature)
        self.assertIsNotNone(dataset.type_distribution)
    
    def test_upload_no_file(self):
        """Test upload endpoint with no file provided."""
        response = self.client.post('/api/datasets/upload/', {})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'No file provided')
    
    def test_upload_non_csv_file(self):
        """Test upload endpoint with non-CSV file."""
        txt_file = io.StringIO("This is a text file")
        txt_file.name = 'test.txt'
        
        response = self.client.post(
            '/api/datasets/upload/',
            {'file': txt_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Invalid file format', response.data['error'])
    
    def test_upload_invalid_csv_missing_columns(self):
        """Test upload with CSV missing required columns."""
        invalid_csv = """Equipment Name,Type,Flowrate
Pump-A1,Pump,150.5"""
        
        csv_file = io.StringIO(invalid_csv)
        csv_file.name = 'invalid.csv'
        
        response = self.client.post(
            '/api/datasets/upload/',
            {'file': csv_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('CSV validation failed', response.data['error'])
    
    def test_upload_invalid_csv_bad_data(self):
        """Test upload with CSV containing invalid numeric data."""
        invalid_csv = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A1,Pump,invalid,45.2,85.0"""
        
        csv_file = io.StringIO(invalid_csv)
        csv_file.name = 'invalid.csv'
        
        response = self.client.post(
            '/api/datasets/upload/',
            {'file': csv_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_upload_unauthenticated(self):
        """Test upload endpoint requires authentication."""
        self.client.credentials()  # Remove authentication
        
        csv_file = io.StringIO(self.valid_csv)
        csv_file.name = 'test.csv'
        
        response = self.client.post(
            '/api/datasets/upload/',
            {'file': csv_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_upload_maintains_history_limit(self):
        """Test that upload maintains the 5 dataset history limit."""
        # Create 5 existing datasets
        for i in range(5):
            Dataset.objects.create(
                name=f'dataset_{i}.csv',
                uploaded_by=self.user,
                total_records=10
            )
        
        # Verify we have 5 datasets
        self.assertEqual(Dataset.objects.filter(uploaded_by=self.user).count(), 5)
        
        # Upload a new dataset
        csv_file = io.StringIO(self.valid_csv)
        csv_file.name = 'new_dataset.csv'
        
        response = self.client.post(
            '/api/datasets/upload/',
            {'file': csv_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify we still have only 5 datasets (oldest was deleted)
        self.assertEqual(Dataset.objects.filter(uploaded_by=self.user).count(), 5)
        
        # Verify the new dataset exists
        self.assertTrue(
            Dataset.objects.filter(uploaded_by=self.user, name='new_dataset.csv').exists()
        )


class DatasetListTests(APITestCase):
    """Test dataset list endpoint functionality."""
    
    def setUp(self):
        """Set up test users and datasets."""
        # Clean up any existing data
        Dataset.objects.all().delete()
        User.objects.all().delete()
        
        self.user1 = User.objects.create_user(username='testuser1', password='testpass123')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass123')
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)
        self.client = APIClient()
    
    def test_list_datasets_returns_last_5(self):
        """Test that list endpoint returns only the last 5 datasets."""
        # Create 7 datasets for user1
        import time
        for i in range(7):
            Dataset.objects.create(
                name=f'dataset_{i}.csv',
                uploaded_by=self.user1,
                total_records=10,
                avg_flowrate=100.0 + i,
                avg_pressure=50.0 + i,
                avg_temperature=75.0 + i,
                type_distribution={'Pump': 5, 'Reactor': 5}
            )
            time.sleep(0.01)  # Small delay to ensure different timestamps
        
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Get list of datasets
        response = self.client.get('/api/datasets/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle paginated response
        if isinstance(response.data, dict) and 'results' in response.data:
            self.assertEqual(len(response.data['results']), 5)
        else:
            self.assertEqual(len(response.data), 5)
    
    def test_list_datasets_ordered_by_uploaded_at_descending(self):
        """Test that datasets are ordered by uploaded_at in descending order."""
        # Create 3 datasets with different timestamps
        import time
        datasets = []
        for i in range(3):
            dataset = Dataset.objects.create(
                name=f'dataset_{i}.csv',
                uploaded_by=self.user1,
                total_records=10,
                avg_flowrate=100.0,
                avg_pressure=50.0,
                avg_temperature=75.0,
                type_distribution={'Pump': 5}
            )
            datasets.append(dataset)
            time.sleep(0.01)  # Small delay to ensure different timestamps
        
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Get list of datasets
        response = self.client.get('/api/datasets/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Handle paginated response
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data
        
        self.assertEqual(len(results), 3)
        
        # Verify order - most recent first
        self.assertEqual(results[0]['name'], 'dataset_2.csv')
        self.assertEqual(results[1]['name'], 'dataset_1.csv')
        self.assertEqual(results[2]['name'], 'dataset_0.csv')
    
    def test_list_datasets_includes_summary_information(self):
        """Test that list endpoint includes all summary information."""
        # Create a dataset with summary statistics
        dataset = Dataset.objects.create(
            name='test_dataset.csv',
            uploaded_by=self.user1,
            total_records=25,
            avg_flowrate=175.5,
            avg_pressure=65.3,
            avg_temperature=195.2,
            type_distribution={'Pump': 8, 'Reactor': 6, 'Heat Exchanger': 7, 'Compressor': 4}
        )
        
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Get list of datasets
        response = self.client.get('/api/datasets/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Handle paginated response
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data
        
        self.assertEqual(len(results), 1)
        
        # Verify all summary information is included
        dataset_data = results[0]
        self.assertEqual(dataset_data['id'], dataset.id)
        self.assertEqual(dataset_data['name'], 'test_dataset.csv')
        self.assertIn('uploaded_at', dataset_data)
        self.assertEqual(dataset_data['total_records'], 25)
        self.assertEqual(dataset_data['avg_flowrate'], 175.5)
        self.assertEqual(dataset_data['avg_pressure'], 65.3)
        self.assertEqual(dataset_data['avg_temperature'], 195.2)
        self.assertEqual(dataset_data['type_distribution'], {
            'Pump': 8, 
            'Reactor': 6, 
            'Heat Exchanger': 7, 
            'Compressor': 4
        })
        self.assertIn('uploaded_by', dataset_data)
    
    def test_list_datasets_user_isolation(self):
        """Test that users only see their own datasets."""
        # Create datasets for both users
        Dataset.objects.create(
            name='user1_dataset.csv',
            uploaded_by=self.user1,
            total_records=10
        )
        Dataset.objects.create(
            name='user2_dataset.csv',
            uploaded_by=self.user2,
            total_records=10
        )
        
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        response = self.client.get('/api/datasets/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Handle paginated response
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'user1_dataset.csv')
        
        # Authenticate as user2
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)
        response = self.client.get('/api/datasets/')
        
        # Handle paginated response
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'user2_dataset.csv')
    
    def test_list_datasets_requires_authentication(self):
        """Test that list endpoint requires authentication."""
        # Create a dataset
        Dataset.objects.create(
            name='test_dataset.csv',
            uploaded_by=self.user1,
            total_records=10
        )
        
        # Try to access without authentication
        self.client.credentials()
        response = self.client.get('/api/datasets/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_datasets_empty_list(self):
        """Test that list endpoint returns empty list when user has no datasets."""
        # Authenticate as user1 (who has no datasets)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Get list of datasets
        response = self.client.get('/api/datasets/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if response is paginated or a list
        if isinstance(response.data, dict) and 'results' in response.data:
            self.assertEqual(len(response.data['results']), 0)
        else:
            self.assertEqual(len(response.data), 0)


class AnalyticsServiceTests(TestCase):
    """Test analytics service functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
        # Create a dataset
        self.dataset = Dataset.objects.create(
            name='test_dataset.csv',
            uploaded_by=self.user,
            total_records=0
        )
        
        # Create equipment records
        EquipmentRecord.objects.create(
            dataset=self.dataset,
            equipment_name='Pump-A1',
            equipment_type='Pump',
            flowrate=150.5,
            pressure=45.2,
            temperature=85.0
        )
        EquipmentRecord.objects.create(
            dataset=self.dataset,
            equipment_name='Reactor-B2',
            equipment_type='Reactor',
            flowrate=200.0,
            pressure=120.5,
            temperature=350.0
        )
        EquipmentRecord.objects.create(
            dataset=self.dataset,
            equipment_name='Heat-Exchanger-C3',
            equipment_type='Heat Exchanger',
            flowrate=180.3,
            pressure=30.0,
            temperature=150.5
        )
        EquipmentRecord.objects.create(
            dataset=self.dataset,
            equipment_name='Pump-A2',
            equipment_type='Pump',
            flowrate=160.0,
            pressure=50.0,
            temperature=90.0
        )
    
    def test_calculate_summary_statistics(self):
        """Test that calculate_summary_statistics returns all statistics at once."""
        service = AnalyticsService(dataset=self.dataset)
        
        summary = service.calculate_summary_statistics()
        
        # Verify structure
        self.assertIn('total_records', summary)
        self.assertIn('avg_flowrate', summary)
        self.assertIn('avg_pressure', summary)
        self.assertIn('avg_temperature', summary)
        self.assertIn('type_distribution', summary)
        
        # Verify total count
        self.assertEqual(summary['total_records'], 4)
        
        # Verify averages (calculated manually)
        # avg_flowrate = (150.5 + 200.0 + 180.3 + 160.0) / 4 = 172.7
        self.assertAlmostEqual(summary['avg_flowrate'], 172.7, places=1)
        
        # avg_pressure = (45.2 + 120.5 + 30.0 + 50.0) / 4 = 61.425
        self.assertAlmostEqual(summary['avg_pressure'], 61.425, places=2)
        
        # avg_temperature = (85.0 + 350.0 + 150.5 + 90.0) / 4 = 168.875
        self.assertAlmostEqual(summary['avg_temperature'], 168.875, places=2)
        
        # Verify type distribution
        self.assertEqual(summary['type_distribution']['Pump'], 2)
        self.assertEqual(summary['type_distribution']['Reactor'], 1)
        self.assertEqual(summary['type_distribution']['Heat Exchanger'], 1)
    
    def test_calculate_summary_statistics_empty_dataset(self):
        """Test calculate_summary_statistics with no records."""
        empty_dataset = Dataset.objects.create(
            name='empty_dataset.csv',
            uploaded_by=self.user,
            total_records=0
        )
        
        service = AnalyticsService(dataset=empty_dataset)
        summary = service.calculate_summary_statistics()
        
        # Verify empty results
        self.assertEqual(summary['total_records'], 0)
        self.assertIsNone(summary['avg_flowrate'])
        self.assertIsNone(summary['avg_pressure'])
        self.assertIsNone(summary['avg_temperature'])
        self.assertEqual(summary['type_distribution'], {})
    
    def test_calculate_summary_statistics_no_dataset(self):
        """Test calculate_summary_statistics with no dataset instance."""
        service = AnalyticsService()
        summary = service.calculate_summary_statistics()
        
        # Verify empty results
        self.assertEqual(summary['total_records'], 0)
        self.assertIsNone(summary['avg_flowrate'])
        self.assertIsNone(summary['avg_pressure'])
        self.assertIsNone(summary['avg_temperature'])
        self.assertEqual(summary['type_distribution'], {})
    
    def test_calculate_summary_statistics_with_queryset(self):
        """Test calculate_summary_statistics with custom queryset."""
        service = AnalyticsService(dataset=self.dataset)
        
        # Only get Pump records
        pump_records = self.dataset.records.filter(equipment_type='Pump')
        summary = service.calculate_summary_statistics(queryset=pump_records)
        
        # Verify only pump records are counted
        self.assertEqual(summary['total_records'], 2)
        
        # Verify averages for pumps only
        # avg_flowrate = (150.5 + 160.0) / 2 = 155.25
        self.assertAlmostEqual(summary['avg_flowrate'], 155.25, places=2)
        
        # Verify type distribution shows only Pump
        self.assertEqual(summary['type_distribution']['Pump'], 2)
        self.assertNotIn('Reactor', summary['type_distribution'])


class DatasetRetrieveTests(APITestCase):
    """Test dataset retrieve endpoint functionality."""
    
    def setUp(self):
        """Set up test users and datasets."""
        self.user1 = User.objects.create_user(username='testuser1', password='testpass123')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass123')
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)
        self.client = APIClient()
        
        # Create a dataset with equipment records for user1
        self.dataset = Dataset.objects.create(
            name='test_dataset.csv',
            uploaded_by=self.user1,
            total_records=3,
            avg_flowrate=176.93,
            avg_pressure=65.23,
            avg_temperature=195.17,
            type_distribution={'Pump': 1, 'Reactor': 1, 'Heat Exchanger': 1}
        )
        
        # Create equipment records
        EquipmentRecord.objects.create(
            dataset=self.dataset,
            equipment_name='Pump-A1',
            equipment_type='Pump',
            flowrate=150.5,
            pressure=45.2,
            temperature=85.0
        )
        EquipmentRecord.objects.create(
            dataset=self.dataset,
            equipment_name='Reactor-B2',
            equipment_type='Reactor',
            flowrate=200.0,
            pressure=120.5,
            temperature=350.0
        )
        EquipmentRecord.objects.create(
            dataset=self.dataset,
            equipment_name='Heat-Exchanger-C3',
            equipment_type='Heat Exchanger',
            flowrate=180.3,
            pressure=30.0,
            temperature=150.5
        )
    
    def test_retrieve_dataset_success(self):
        """Test successful retrieval of a specific dataset."""
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Retrieve the dataset
        response = self.client.get(f'/api/datasets/{self.dataset.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify dataset details are returned
        self.assertEqual(response.data['id'], self.dataset.id)
        self.assertEqual(response.data['name'], 'test_dataset.csv')
        self.assertEqual(response.data['total_records'], 3)
        self.assertAlmostEqual(response.data['avg_flowrate'], 176.93, places=2)
        self.assertAlmostEqual(response.data['avg_pressure'], 65.23, places=2)
        self.assertAlmostEqual(response.data['avg_temperature'], 195.17, places=2)
        self.assertEqual(response.data['type_distribution'], {
            'Pump': 1, 
            'Reactor': 1, 
            'Heat Exchanger': 1
        })
        
        # Verify uploaded_by information is included
        self.assertIn('uploaded_by', response.data)
        self.assertEqual(response.data['uploaded_by']['username'], 'testuser1')
        
        # Verify uploaded_at is included
        self.assertIn('uploaded_at', response.data)
    
    def test_retrieve_dataset_includes_summary_statistics(self):
        """Test that retrieve endpoint includes all summary statistics."""
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Retrieve the dataset
        response = self.client.get(f'/api/datasets/{self.dataset.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify all summary statistics are present
        required_fields = [
            'id', 'name', 'uploaded_at', 'uploaded_by', 'total_records',
            'avg_flowrate', 'avg_pressure', 'avg_temperature', 'type_distribution'
        ]
        
        for field in required_fields:
            self.assertIn(field, response.data, f"Field '{field}' should be in response")
    
    def test_retrieve_dataset_not_found(self):
        """Test retrieval of non-existent dataset returns 404."""
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Try to retrieve a dataset that doesn't exist
        response = self.client.get('/api/datasets/99999/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_retrieve_dataset_requires_authentication(self):
        """Test that retrieve endpoint requires authentication."""
        # Try to retrieve without authentication
        self.client.credentials()
        response = self.client.get(f'/api/datasets/{self.dataset.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_retrieve_dataset_user_isolation(self):
        """Test that users cannot retrieve other users' datasets."""
        # Create a dataset for user2
        user2_dataset = Dataset.objects.create(
            name='user2_dataset.csv',
            uploaded_by=self.user2,
            total_records=5,
            avg_flowrate=150.0,
            avg_pressure=50.0,
            avg_temperature=100.0,
            type_distribution={'Pump': 5}
        )
        
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Try to retrieve user2's dataset
        response = self.client.get(f'/api/datasets/{user2_dataset.id}/')
        
        # Should return 404 (not found) to prevent information leakage
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_retrieve_dataset_owner_can_access(self):
        """Test that dataset owner can successfully retrieve their dataset."""
        # Authenticate as user1 (owner)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Retrieve own dataset
        response = self.client.get(f'/api/datasets/{self.dataset.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.dataset.id)



class DatasetDataEndpointTests(APITestCase):
    """Test dataset data endpoint functionality (GET /api/datasets/{id}/data/)."""
    
    def setUp(self):
        """Set up test users and datasets."""
        self.user1 = User.objects.create_user(username='testuser1', password='testpass123')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass123')
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)
        self.client = APIClient()
        
        # Create a dataset with equipment records for user1
        self.dataset = Dataset.objects.create(
            name='test_dataset.csv',
            uploaded_by=self.user1,
            total_records=3,
            avg_flowrate=176.93,
            avg_pressure=65.23,
            avg_temperature=195.17,
            type_distribution={'Pump': 1, 'Reactor': 1, 'Heat Exchanger': 1}
        )
        
        # Create equipment records
        self.records = []
        for i in range(3):
            record = EquipmentRecord.objects.create(
                dataset=self.dataset,
                equipment_name=f'Equipment-{i}',
                equipment_type='Pump' if i == 0 else 'Reactor',
                flowrate=150.5 + i * 10,
                pressure=45.2 + i * 5,
                temperature=85.0 + i * 20
            )
            self.records.append(record)
    
    def test_data_endpoint_returns_all_records(self):
        """Test that data endpoint returns all equipment records for a dataset."""
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Get equipment records
        response = self.client.get(f'/api/datasets/{self.dataset.id}/data/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check paginated response structure
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        
        # Verify all records are returned
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(len(response.data['results']), 3)
        
        # Verify record structure
        first_record = response.data['results'][0]
        self.assertIn('id', first_record)
        self.assertIn('equipment_name', first_record)
        self.assertIn('equipment_type', first_record)
        self.assertIn('flowrate', first_record)
        self.assertIn('pressure', first_record)
        self.assertIn('temperature', first_record)
    
    def test_data_endpoint_pagination(self):
        """Test that data endpoint supports pagination."""
        # Create a dataset with many records
        large_dataset = Dataset.objects.create(
            name='large_dataset.csv',
            uploaded_by=self.user1,
            total_records=100
        )
        
        # Create 100 equipment records
        for i in range(100):
            EquipmentRecord.objects.create(
                dataset=large_dataset,
                equipment_name=f'Equipment-{i}',
                equipment_type='Pump',
                flowrate=150.0 + i,
                pressure=45.0 + i,
                temperature=85.0 + i
            )
        
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Get first page (default page size is 50)
        response = self.client.get(f'/api/datasets/{large_dataset.id}/data/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 100)
        self.assertEqual(len(response.data['results']), 50)
        
        # Verify pagination links
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIsNotNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        
        # Get second page
        response = self.client.get(f'/api/datasets/{large_dataset.id}/data/?page=2')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 50)
        self.assertIsNone(response.data['next'])
        self.assertIsNotNone(response.data['previous'])
    
    def test_data_endpoint_custom_page_size(self):
        """Test that data endpoint supports custom page size."""
        # Create a dataset with 30 records
        dataset = Dataset.objects.create(
            name='dataset.csv',
            uploaded_by=self.user1,
            total_records=30
        )
        
        for i in range(30):
            EquipmentRecord.objects.create(
                dataset=dataset,
                equipment_name=f'Equipment-{i}',
                equipment_type='Pump',
                flowrate=150.0,
                pressure=45.0,
                temperature=85.0
            )
        
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Request with custom page size
        response = self.client.get(f'/api/datasets/{dataset.id}/data/?page_size=10')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 30)
        self.assertEqual(len(response.data['results']), 10)
    
    def test_data_endpoint_requires_authentication(self):
        """Test that data endpoint requires authentication."""
        # Try to access without authentication
        self.client.credentials()
        response = self.client.get(f'/api/datasets/{self.dataset.id}/data/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_data_endpoint_user_isolation(self):
        """Test that users cannot access other users' dataset records."""
        # Create a dataset for user2
        user2_dataset = Dataset.objects.create(
            name='user2_dataset.csv',
            uploaded_by=self.user2,
            total_records=2
        )
        
        EquipmentRecord.objects.create(
            dataset=user2_dataset,
            equipment_name='User2-Equipment',
            equipment_type='Pump',
            flowrate=150.0,
            pressure=45.0,
            temperature=85.0
        )
        
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Try to access user2's dataset records
        response = self.client.get(f'/api/datasets/{user2_dataset.id}/data/')
        
        # Should return 404 (not found) to prevent information leakage
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_data_endpoint_dataset_not_found(self):
        """Test that data endpoint returns 404 for non-existent dataset."""
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Try to access non-existent dataset
        response = self.client.get('/api/datasets/99999/data/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_data_endpoint_empty_dataset(self):
        """Test that data endpoint handles datasets with no records."""
        # Create a dataset with no records
        empty_dataset = Dataset.objects.create(
            name='empty_dataset.csv',
            uploaded_by=self.user1,
            total_records=0
        )
        
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Get equipment records
        response = self.client.get(f'/api/datasets/{empty_dataset.id}/data/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['results']), 0)


class DatasetSummaryEndpointTests(APITestCase):
    """Test dataset summary endpoint functionality (GET /api/datasets/{id}/summary/)."""
    
    def setUp(self):
        """Set up test users and datasets."""
        self.user1 = User.objects.create_user(username='testuser1', password='testpass123')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass123')
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)
        self.client = APIClient()
        
        # Create a dataset with equipment records for user1
        self.dataset = Dataset.objects.create(
            name='test_dataset.csv',
            uploaded_by=self.user1,
            total_records=4,
            avg_flowrate=172.7,
            avg_pressure=61.425,
            avg_temperature=168.875,
            type_distribution={'Pump': 2, 'Reactor': 1, 'Heat Exchanger': 1}
        )
        
        # Create equipment records
        EquipmentRecord.objects.create(
            dataset=self.dataset,
            equipment_name='Pump-A1',
            equipment_type='Pump',
            flowrate=150.5,
            pressure=45.2,
            temperature=85.0
        )
        EquipmentRecord.objects.create(
            dataset=self.dataset,
            equipment_name='Reactor-B2',
            equipment_type='Reactor',
            flowrate=200.0,
            pressure=120.5,
            temperature=350.0
        )
        EquipmentRecord.objects.create(
            dataset=self.dataset,
            equipment_name='Heat-Exchanger-C3',
            equipment_type='Heat Exchanger',
            flowrate=180.3,
            pressure=30.0,
            temperature=150.5
        )
        EquipmentRecord.objects.create(
            dataset=self.dataset,
            equipment_name='Pump-A2',
            equipment_type='Pump',
            flowrate=160.0,
            pressure=50.0,
            temperature=90.0
        )
    
    def test_summary_endpoint_returns_calculated_statistics(self):
        """Test that summary endpoint returns all calculated summary statistics."""
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Get summary statistics
        response = self.client.get(f'/api/datasets/{self.dataset.id}/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify all summary fields are present
        self.assertIn('id', response.data)
        self.assertIn('name', response.data)
        self.assertIn('uploaded_at', response.data)
        self.assertIn('total_records', response.data)
        self.assertIn('avg_flowrate', response.data)
        self.assertIn('avg_pressure', response.data)
        self.assertIn('avg_temperature', response.data)
        self.assertIn('type_distribution', response.data)
        
        # Verify values
        self.assertEqual(response.data['id'], self.dataset.id)
        self.assertEqual(response.data['name'], 'test_dataset.csv')
        self.assertEqual(response.data['total_records'], 4)
        self.assertAlmostEqual(response.data['avg_flowrate'], 172.7, places=1)
        self.assertAlmostEqual(response.data['avg_pressure'], 61.425, places=2)
        self.assertAlmostEqual(response.data['avg_temperature'], 168.875, places=2)
    
    def test_summary_endpoint_includes_type_distribution(self):
        """Test that summary endpoint includes equipment type distribution data."""
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Get summary statistics
        response = self.client.get(f'/api/datasets/{self.dataset.id}/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify type distribution
        self.assertIn('type_distribution', response.data)
        type_dist = response.data['type_distribution']
        
        self.assertEqual(type_dist['Pump'], 2)
        self.assertEqual(type_dist['Reactor'], 1)
        self.assertEqual(type_dist['Heat Exchanger'], 1)
        self.assertEqual(len(type_dist), 3)
    
    def test_summary_endpoint_requires_authentication(self):
        """Test that summary endpoint requires authentication."""
        # Try to access without authentication
        self.client.credentials()
        response = self.client.get(f'/api/datasets/{self.dataset.id}/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_summary_endpoint_user_isolation(self):
        """Test that users cannot access other users' dataset summaries."""
        # Create a dataset for user2
        user2_dataset = Dataset.objects.create(
            name='user2_dataset.csv',
            uploaded_by=self.user2,
            total_records=5,
            avg_flowrate=150.0,
            avg_pressure=50.0,
            avg_temperature=100.0,
            type_distribution={'Pump': 5}
        )
        
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Try to access user2's dataset summary
        response = self.client.get(f'/api/datasets/{user2_dataset.id}/summary/')
        
        # Should return 404 (not found) to prevent information leakage
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_summary_endpoint_dataset_not_found(self):
        """Test that summary endpoint returns 404 for non-existent dataset."""
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Try to access non-existent dataset
        response = self.client.get('/api/datasets/99999/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_summary_endpoint_empty_dataset(self):
        """Test that summary endpoint handles datasets with no records."""
        # Create a dataset with no records
        empty_dataset = Dataset.objects.create(
            name='empty_dataset.csv',
            uploaded_by=self.user1,
            total_records=0,
            avg_flowrate=None,
            avg_pressure=None,
            avg_temperature=None,
            type_distribution={}
        )
        
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Get summary statistics
        response = self.client.get(f'/api/datasets/{empty_dataset.id}/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_records'], 0)
        self.assertIsNone(response.data['avg_flowrate'])
        self.assertIsNone(response.data['avg_pressure'])
        self.assertIsNone(response.data['avg_temperature'])
        self.assertEqual(response.data['type_distribution'], {})
    
    def test_summary_endpoint_owner_can_access(self):
        """Test that dataset owner can successfully retrieve summary."""
        # Authenticate as user1 (owner)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Retrieve own dataset summary
        response = self.client.get(f'/api/datasets/{self.dataset.id}/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.dataset.id)
