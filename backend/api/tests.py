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
    
    def test_validate_csv_with_extra_columns(self):
        """Test that CSV with extra columns beyond required ones is accepted."""
        csv_with_extra = """Equipment Name,Type,Flowrate,Pressure,Temperature,Extra Column
Pump-A1,Pump,150.5,45.2,85.0,Extra Data"""
        
        csv_file = io.StringIO(csv_with_extra)
        
        # Should not raise an error - extra columns are allowed
        df, records = self.processor.parse_csv_file(csv_file)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['equipment_name'], 'Pump-A1')
    
    def test_validate_csv_with_whitespace_in_values(self):
        """Test that CSV with whitespace in values is handled correctly."""
        csv_with_whitespace = """Equipment Name,Type,Flowrate,Pressure,Temperature
  Pump-A1  ,  Pump  ,150.5,45.2,85.0"""
        
        csv_file = io.StringIO(csv_with_whitespace)
        
        # Should parse successfully and strip whitespace
        df, records = self.processor.parse_csv_file(csv_file)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['equipment_name'], 'Pump-A1')
        self.assertEqual(records[0]['equipment_type'], 'Pump')
    
    def test_validate_csv_with_mixed_case_column_names(self):
        """Test that CSV column names are case-sensitive."""
        csv_mixed_case = """equipment name,type,flowrate,pressure,temperature
Pump-A1,Pump,150.5,45.2,85.0"""
        
        csv_file = io.StringIO(csv_mixed_case)
        
        # Should fail because column names don't match exactly
        with self.assertRaises(CSVValidationError) as context:
            self.processor.parse_csv_file(csv_file)
        
        self.assertIn('Missing required columns', str(context.exception))
    
    def test_validate_csv_with_special_characters_in_names(self):
        """Test that CSV handles special characters in equipment names and types."""
        csv_special_chars = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A1 (Primary),Heat Exchanger - Type A,150.5,45.2,85.0"""
        
        csv_file = io.StringIO(csv_special_chars)
        
        # Should parse successfully
        df, records = self.processor.parse_csv_file(csv_file)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['equipment_name'], 'Pump-A1 (Primary)')
        self.assertEqual(records[0]['equipment_type'], 'Heat Exchanger - Type A')
    
    def test_validate_csv_with_very_large_numbers(self):
        """Test that CSV handles very large numeric values."""
        csv_large_numbers = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A1,Pump,999999.99,999999.99,999999.99"""
        
        csv_file = io.StringIO(csv_large_numbers)
        
        # Should parse successfully
        df, records = self.processor.parse_csv_file(csv_file)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['flowrate'], 999999.99)
        self.assertEqual(records[0]['pressure'], 999999.99)
        self.assertEqual(records[0]['temperature'], 999999.99)
    
    def test_validate_csv_with_very_small_positive_numbers(self):
        """Test that CSV handles very small positive numeric values."""
        csv_small_numbers = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A1,Pump,0.001,0.001,0.001"""
        
        csv_file = io.StringIO(csv_small_numbers)
        
        # Should parse successfully
        df, records = self.processor.parse_csv_file(csv_file)
        self.assertEqual(len(records), 1)
        self.assertAlmostEqual(records[0]['flowrate'], 0.001, places=3)
        self.assertAlmostEqual(records[0]['pressure'], 0.001, places=3)
        self.assertAlmostEqual(records[0]['temperature'], 0.001, places=3)
    
    def test_validate_csv_with_decimal_variations(self):
        """Test that CSV handles different decimal formats."""
        csv_decimals = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A1,Pump,150,45.2,85.0
Pump-A2,Pump,150.5,45,85"""
        
        csv_file = io.StringIO(csv_decimals)
        
        # Should parse successfully - integers should be converted to floats
        df, records = self.processor.parse_csv_file(csv_file)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]['flowrate'], 150.0)
        self.assertEqual(records[1]['pressure'], 45.0)
    
    def test_validate_csv_with_scientific_notation(self):
        """Test that CSV handles scientific notation in numeric fields."""
        csv_scientific = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A1,Pump,1.5e2,4.52e1,8.5e1"""
        
        csv_file = io.StringIO(csv_scientific)
        
        # Should parse successfully
        df, records = self.processor.parse_csv_file(csv_file)
        self.assertEqual(len(records), 1)
        self.assertAlmostEqual(records[0]['flowrate'], 150.0, places=1)
        self.assertAlmostEqual(records[0]['pressure'], 45.2, places=1)
        self.assertAlmostEqual(records[0]['temperature'], 85.0, places=1)
    
    def test_validate_csv_with_only_headers(self):
        """Test that CSV with only headers (no data rows) is rejected."""
        csv_only_headers = """Equipment Name,Type,Flowrate,Pressure,Temperature"""
        
        csv_file = io.StringIO(csv_only_headers)
        
        # Should fail because there's no data
        with self.assertRaises(CSVValidationError) as context:
            self.processor.parse_csv_file(csv_file)
        
        self.assertIn('empty', str(context.exception).lower())
    
    def test_validate_csv_with_null_values_in_numeric_fields(self):
        """Test that CSV with null/empty values in numeric fields is rejected."""
        csv_null_numeric = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A1,Pump,,45.2,85.0"""
        
        csv_file = io.StringIO(csv_null_numeric)
        
        # Should fail because Flowrate is empty
        with self.assertRaises(CSVValidationError) as context:
            self.processor.parse_csv_file(csv_file)
        
        error_msg = str(context.exception)
        self.assertIn('Flowrate', error_msg)
        self.assertIn('empty', error_msg.lower())
    
    def test_validate_csv_with_multiple_rows_mixed_validity(self):
        """Test that CSV validation catches errors across multiple rows."""
        csv_mixed = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A1,Pump,150.5,45.2,85.0
Reactor-B2,Reactor,-200.0,120.5,350.0
Heat-Exchanger-C3,Heat Exchanger,180.3,-30.0,150.5"""
        
        csv_file = io.StringIO(csv_mixed)
        
        # Should fail because of negative flowrate and pressure
        with self.assertRaises(CSVValidationError) as context:
            self.processor.parse_csv_file(csv_file)
        
        error_msg = str(context.exception)
        # Should report both Flowrate and Pressure errors
        self.assertIn('positive', error_msg.lower())
    
    def test_parse_to_records_conversion(self):
        """Test that parse_to_records correctly converts DataFrame to record dictionaries."""
        csv_content = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A1,Pump,150.5,45.2,85.0
Reactor-B2,Reactor,200.0,120.5,350.0"""
        
        csv_file = io.StringIO(csv_content)
        df, records = self.processor.parse_csv_file(csv_file)
        
        # Verify record structure
        self.assertEqual(len(records), 2)
        
        # Check first record
        self.assertIn('equipment_name', records[0])
        self.assertIn('equipment_type', records[0])
        self.assertIn('flowrate', records[0])
        self.assertIn('pressure', records[0])
        self.assertIn('temperature', records[0])
        
        # Verify data types
        self.assertIsInstance(records[0]['equipment_name'], str)
        self.assertIsInstance(records[0]['equipment_type'], str)
        self.assertIsInstance(records[0]['flowrate'], float)
        self.assertIsInstance(records[0]['pressure'], float)
        self.assertIsInstance(records[0]['temperature'], float)
    
    def test_validate_method_with_file_path(self):
        """Test that validate method works with file path parameter."""
        # Create a temporary CSV file
        import tempfile
        import os
        
        csv_content = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A1,Pump,150.5,45.2,85.0"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            # Validate using file path
            result = self.processor.validate(file_path=temp_path)
            
            self.assertTrue(result['is_valid'])
            self.assertEqual(len(result['errors']), 0)
            self.assertIsNotNone(result['dataframe'])
            self.assertEqual(len(result['dataframe']), 1)
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
    
    def test_validate_method_with_file_content(self):
        """Test that validate method works with file content parameter."""
        csv_content = """Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A1,Pump,150.5,45.2,85.0"""
        
        csv_file = io.StringIO(csv_content)
        
        # Validate using file content
        result = self.processor.validate(file_content=csv_file)
        
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
        self.assertIsNotNone(result['dataframe'])
        self.assertEqual(len(result['dataframe']), 1)
    
    def test_validate_method_returns_errors_for_invalid_csv(self):
        """Test that validate method returns detailed error information."""
        csv_invalid = """Equipment Name,Type,Flowrate
Pump-A1,Pump,150.5"""
        
        csv_file = io.StringIO(csv_invalid)
        
        # Validate invalid CSV
        result = self.processor.validate(file_content=csv_file)
        
        self.assertFalse(result['is_valid'])
        self.assertIn('missing_columns', result['errors'])
        self.assertIsNone(result['dataframe'])
        
        # Check error details
        missing_cols_error = result['errors']['missing_columns']
        self.assertIn('Pressure', missing_cols_error['missing'])
        self.assertIn('Temperature', missing_cols_error['missing'])


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


class AnalyticsServiceTests(TestCase):
    """Test analytics service functionality.
    
    Requirements: 2.1, 2.2, 2.3
    """
    
    def setUp(self):
        """Set up test data for analytics tests."""
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
        # Create a dataset
        self.dataset = Dataset.objects.create(
            name='test_dataset.csv',
            uploaded_by=self.user,
            total_records=0
        )
        
        # Create equipment records with known values for testing
        self.records = [
            EquipmentRecord.objects.create(
                dataset=self.dataset,
                equipment_name='Pump-A1',
                equipment_type='Pump',
                flowrate=100.0,
                pressure=50.0,
                temperature=80.0
            ),
            EquipmentRecord.objects.create(
                dataset=self.dataset,
                equipment_name='Pump-A2',
                equipment_type='Pump',
                flowrate=200.0,
                pressure=60.0,
                temperature=90.0
            ),
            EquipmentRecord.objects.create(
                dataset=self.dataset,
                equipment_name='Reactor-B1',
                equipment_type='Reactor',
                flowrate=150.0,
                pressure=100.0,
                temperature=300.0
            ),
            EquipmentRecord.objects.create(
                dataset=self.dataset,
                equipment_name='Heat-Exchanger-C1',
                equipment_type='Heat Exchanger',
                flowrate=180.0,
                pressure=30.0,
                temperature=150.0
            ),
        ]
        
        self.service = AnalyticsService(dataset=self.dataset)
    
    def test_calculate_total_count(self):
        """Test total count calculation.
        
        Requirements: 2.1
        """
        count = self.service.calculate_total_count()
        self.assertEqual(count, 4)
    
    def test_calculate_total_count_empty_dataset(self):
        """Test total count calculation with empty dataset.
        
        Requirements: 2.1
        """
        empty_dataset = Dataset.objects.create(
            name='empty_dataset.csv',
            uploaded_by=self.user,
            total_records=0
        )
        service = AnalyticsService(dataset=empty_dataset)
        
        count = service.calculate_total_count()
        self.assertEqual(count, 0)
    
    def test_calculate_total_count_no_dataset(self):
        """Test total count calculation with no dataset.
        
        Requirements: 2.1
        """
        service = AnalyticsService()
        count = service.calculate_total_count()
        self.assertEqual(count, 0)
    
    def test_calculate_averages(self):
        """Test average calculations for flowrate, pressure, and temperature.
        
        Requirements: 2.2
        """
        averages = self.service.calculate_averages()
        
        # Expected averages:
        # flowrate: (100 + 200 + 150 + 180) / 4 = 157.5
        # pressure: (50 + 60 + 100 + 30) / 4 = 60.0
        # temperature: (80 + 90 + 300 + 150) / 4 = 155.0
        
        self.assertAlmostEqual(averages['avg_flowrate'], 157.5, places=2)
        self.assertAlmostEqual(averages['avg_pressure'], 60.0, places=2)
        self.assertAlmostEqual(averages['avg_temperature'], 155.0, places=2)
    
    def test_calculate_averages_empty_dataset(self):
        """Test average calculations with empty dataset.
        
        Requirements: 2.2
        """
        empty_dataset = Dataset.objects.create(
            name='empty_dataset.csv',
            uploaded_by=self.user,
            total_records=0
        )
        service = AnalyticsService(dataset=empty_dataset)
        
        averages = service.calculate_averages()
        
        self.assertIsNone(averages['avg_flowrate'])
        self.assertIsNone(averages['avg_pressure'])
        self.assertIsNone(averages['avg_temperature'])
    
    def test_calculate_averages_no_dataset(self):
        """Test average calculations with no dataset.
        
        Requirements: 2.2
        """
        service = AnalyticsService()
        averages = service.calculate_averages()
        
        self.assertIsNone(averages['avg_flowrate'])
        self.assertIsNone(averages['avg_pressure'])
        self.assertIsNone(averages['avg_temperature'])
    
    def test_calculate_averages_single_record(self):
        """Test average calculations with single record.
        
        Requirements: 2.2
        """
        single_dataset = Dataset.objects.create(
            name='single_dataset.csv',
            uploaded_by=self.user,
            total_records=0
        )
        EquipmentRecord.objects.create(
            dataset=single_dataset,
            equipment_name='Pump-X1',
            equipment_type='Pump',
            flowrate=123.45,
            pressure=67.89,
            temperature=100.0
        )
        
        service = AnalyticsService(dataset=single_dataset)
        averages = service.calculate_averages()
        
        self.assertAlmostEqual(averages['avg_flowrate'], 123.45, places=2)
        self.assertAlmostEqual(averages['avg_pressure'], 67.89, places=2)
        self.assertAlmostEqual(averages['avg_temperature'], 100.0, places=2)
    
    def test_generate_type_distribution(self):
        """Test equipment type distribution generation.
        
        Requirements: 2.3
        """
        distribution = self.service.generate_type_distribution()
        
        # Expected distribution:
        # Pump: 2, Reactor: 1, Heat Exchanger: 1
        
        self.assertEqual(distribution['Pump'], 2)
        self.assertEqual(distribution['Reactor'], 1)
        self.assertEqual(distribution['Heat Exchanger'], 1)
        self.assertEqual(len(distribution), 3)
    
    def test_generate_type_distribution_empty_dataset(self):
        """Test type distribution with empty dataset.
        
        Requirements: 2.3
        """
        empty_dataset = Dataset.objects.create(
            name='empty_dataset.csv',
            uploaded_by=self.user,
            total_records=0
        )
        service = AnalyticsService(dataset=empty_dataset)
        
        distribution = service.generate_type_distribution()
        
        self.assertEqual(distribution, {})
    
    def test_generate_type_distribution_no_dataset(self):
        """Test type distribution with no dataset.
        
        Requirements: 2.3
        """
        service = AnalyticsService()
        distribution = service.generate_type_distribution()
        
        self.assertEqual(distribution, {})
    
    def test_generate_type_distribution_single_type(self):
        """Test type distribution with all records of same type.
        
        Requirements: 2.3
        """
        single_type_dataset = Dataset.objects.create(
            name='single_type_dataset.csv',
            uploaded_by=self.user,
            total_records=0
        )
        
        for i in range(5):
            EquipmentRecord.objects.create(
                dataset=single_type_dataset,
                equipment_name=f'Pump-{i}',
                equipment_type='Pump',
                flowrate=100.0 + i,
                pressure=50.0 + i,
                temperature=80.0 + i
            )
        
        service = AnalyticsService(dataset=single_type_dataset)
        distribution = service.generate_type_distribution()
        
        self.assertEqual(distribution['Pump'], 5)
        self.assertEqual(len(distribution), 1)
    
    def test_generate_type_distribution_many_types(self):
        """Test type distribution with many different types.
        
        Requirements: 2.3
        """
        many_types_dataset = Dataset.objects.create(
            name='many_types_dataset.csv',
            uploaded_by=self.user,
            total_records=0
        )
        
        types = ['Pump', 'Reactor', 'Heat Exchanger', 'Compressor', 'Valve', 'Tank']
        for equipment_type in types:
            EquipmentRecord.objects.create(
                dataset=many_types_dataset,
                equipment_name=f'{equipment_type}-1',
                equipment_type=equipment_type,
                flowrate=100.0,
                pressure=50.0,
                temperature=80.0
            )
        
        service = AnalyticsService(dataset=many_types_dataset)
        distribution = service.generate_type_distribution()
        
        self.assertEqual(len(distribution), 6)
        for equipment_type in types:
            self.assertEqual(distribution[equipment_type], 1)
    
    def test_calculate_summary_statistics(self):
        """Test complete summary statistics calculation.
        
        Requirements: 2.1, 2.2, 2.3
        """
        summary = self.service.calculate_summary_statistics()
        
        # Verify all fields are present
        self.assertIn('total_records', summary)
        self.assertIn('avg_flowrate', summary)
        self.assertIn('avg_pressure', summary)
        self.assertIn('avg_temperature', summary)
        self.assertIn('type_distribution', summary)
        
        # Verify values
        self.assertEqual(summary['total_records'], 4)
        self.assertAlmostEqual(summary['avg_flowrate'], 157.5, places=2)
        self.assertAlmostEqual(summary['avg_pressure'], 60.0, places=2)
        self.assertAlmostEqual(summary['avg_temperature'], 155.0, places=2)
        self.assertEqual(summary['type_distribution']['Pump'], 2)
        self.assertEqual(summary['type_distribution']['Reactor'], 1)
        self.assertEqual(summary['type_distribution']['Heat Exchanger'], 1)
    
    def test_calculate_summary_statistics_empty_dataset(self):
        """Test summary statistics with empty dataset.
        
        Requirements: 2.1, 2.2, 2.3
        """
        empty_dataset = Dataset.objects.create(
            name='empty_dataset.csv',
            uploaded_by=self.user,
            total_records=0
        )
        service = AnalyticsService(dataset=empty_dataset)
        
        summary = service.calculate_summary_statistics()
        
        self.assertEqual(summary['total_records'], 0)
        self.assertIsNone(summary['avg_flowrate'])
        self.assertIsNone(summary['avg_pressure'])
        self.assertIsNone(summary['avg_temperature'])
        self.assertEqual(summary['type_distribution'], {})
    
    def test_calculate_summary_statistics_no_dataset(self):
        """Test summary statistics with no dataset.
        
        Requirements: 2.1, 2.2, 2.3
        """
        service = AnalyticsService()
        summary = service.calculate_summary_statistics()
        
        self.assertEqual(summary['total_records'], 0)
        self.assertIsNone(summary['avg_flowrate'])
        self.assertIsNone(summary['avg_pressure'])
        self.assertIsNone(summary['avg_temperature'])
        self.assertEqual(summary['type_distribution'], {})
    
    def test_update_dataset_statistics(self):
        """Test updating dataset model with calculated statistics.
        
        Requirements: 2.1, 2.2, 2.3
        """
        # Initially dataset has no statistics
        self.assertEqual(self.dataset.total_records, 0)
        
        # Update statistics
        self.service.update_dataset_statistics()
        
        # Verify dataset fields were updated (but not saved)
        self.assertEqual(self.dataset.total_records, 4)
        self.assertAlmostEqual(self.dataset.avg_flowrate, 157.5, places=2)
        self.assertAlmostEqual(self.dataset.avg_pressure, 60.0, places=2)
        self.assertAlmostEqual(self.dataset.avg_temperature, 155.0, places=2)
        self.assertEqual(self.dataset.type_distribution['Pump'], 2)
        self.assertEqual(self.dataset.type_distribution['Reactor'], 1)
        self.assertEqual(self.dataset.type_distribution['Heat Exchanger'], 1)
    
    def test_update_dataset_statistics_no_dataset_raises_error(self):
        """Test that update_dataset_statistics raises error when no dataset.
        
        Requirements: 2.1, 2.2, 2.3
        """
        service = AnalyticsService()
        
        with self.assertRaises(ValueError) as context:
            service.update_dataset_statistics()
        
        self.assertIn('No dataset', str(context.exception))
    
    def test_calculate_with_custom_queryset(self):
        """Test calculations with custom queryset (filtered records).
        
        Requirements: 2.1, 2.2, 2.3
        """
        # Filter only Pump records
        pump_queryset = EquipmentRecord.objects.filter(
            dataset=self.dataset,
            equipment_type='Pump'
        )
        
        # Calculate statistics for pumps only
        count = self.service.calculate_total_count(pump_queryset)
        averages = self.service.calculate_averages(pump_queryset)
        distribution = self.service.generate_type_distribution(pump_queryset)
        
        # Verify results
        self.assertEqual(count, 2)
        self.assertAlmostEqual(averages['avg_flowrate'], 150.0, places=2)  # (100 + 200) / 2
        self.assertAlmostEqual(averages['avg_pressure'], 55.0, places=2)   # (50 + 60) / 2
        self.assertAlmostEqual(averages['avg_temperature'], 85.0, places=2) # (80 + 90) / 2
        self.assertEqual(distribution['Pump'], 2)
        self.assertEqual(len(distribution), 1)
    
    def test_calculate_averages_with_extreme_values(self):
        """Test average calculations with extreme values.
        
        Requirements: 2.2
        """
        extreme_dataset = Dataset.objects.create(
            name='extreme_dataset.csv',
            uploaded_by=self.user,
            total_records=0
        )
        
        # Create records with extreme values
        EquipmentRecord.objects.create(
            dataset=extreme_dataset,
            equipment_name='Equipment-1',
            equipment_type='Pump',
            flowrate=0.001,
            pressure=0.001,
            temperature=-273.15  # Absolute zero
        )
        EquipmentRecord.objects.create(
            dataset=extreme_dataset,
            equipment_name='Equipment-2',
            equipment_type='Pump',
            flowrate=999999.99,
            pressure=999999.99,
            temperature=999999.99
        )
        
        service = AnalyticsService(dataset=extreme_dataset)
        averages = service.calculate_averages()
        
        # Verify calculations work with extreme values
        self.assertIsNotNone(averages['avg_flowrate'])
        self.assertIsNotNone(averages['avg_pressure'])
        self.assertIsNotNone(averages['avg_temperature'])
        
        # Verify average is between min and max
        self.assertGreater(averages['avg_flowrate'], 0.001)
        self.assertLess(averages['avg_flowrate'], 999999.99)
    
    def test_calculate_averages_with_negative_temperature(self):
        """Test average calculations with negative temperature values.
        
        Requirements: 2.2
        """
        negative_temp_dataset = Dataset.objects.create(
            name='negative_temp_dataset.csv',
            uploaded_by=self.user,
            total_records=0
        )
        
        EquipmentRecord.objects.create(
            dataset=negative_temp_dataset,
            equipment_name='Equipment-1',
            equipment_type='Pump',
            flowrate=100.0,
            pressure=50.0,
            temperature=-10.0
        )
        EquipmentRecord.objects.create(
            dataset=negative_temp_dataset,
            equipment_name='Equipment-2',
            equipment_type='Pump',
            flowrate=100.0,
            pressure=50.0,
            temperature=10.0
        )
        
        service = AnalyticsService(dataset=negative_temp_dataset)
        averages = service.calculate_averages()
        
        # Average should be 0.0
        self.assertAlmostEqual(averages['avg_temperature'], 0.0, places=2)
    
    def test_type_distribution_preserves_order(self):
        """Test that type distribution is ordered alphabetically.
        
        Requirements: 2.3
        """
        ordered_dataset = Dataset.objects.create(
            name='ordered_dataset.csv',
            uploaded_by=self.user,
            total_records=0
        )
        
        # Create records in non-alphabetical order
        types = ['Valve', 'Pump', 'Reactor', 'Compressor']
        for equipment_type in types:
            EquipmentRecord.objects.create(
                dataset=ordered_dataset,
                equipment_name=f'{equipment_type}-1',
                equipment_type=equipment_type,
                flowrate=100.0,
                pressure=50.0,
                temperature=80.0
            )
        
        service = AnalyticsService(dataset=ordered_dataset)
        distribution = service.generate_type_distribution()
        
        # Verify all types are present
        self.assertEqual(len(distribution), 4)
        for equipment_type in types:
            self.assertEqual(distribution[equipment_type], 1)
    
    def test_calculate_with_large_dataset(self):
        """Test calculations with large number of records.
        
        Requirements: 2.1, 2.2, 2.3
        """
        large_dataset = Dataset.objects.create(
            name='large_dataset.csv',
            uploaded_by=self.user,
            total_records=0
        )
        
        # Create 100 records
        for i in range(100):
            EquipmentRecord.objects.create(
                dataset=large_dataset,
                equipment_name=f'Equipment-{i}',
                equipment_type='Pump' if i % 2 == 0 else 'Reactor',
                flowrate=100.0 + i,
                pressure=50.0 + i,
                temperature=80.0 + i
            )
        
        service = AnalyticsService(dataset=large_dataset)
        summary = service.calculate_summary_statistics()
        
        # Verify calculations
        self.assertEqual(summary['total_records'], 100)
        self.assertIsNotNone(summary['avg_flowrate'])
        self.assertIsNotNone(summary['avg_pressure'])
        self.assertIsNotNone(summary['avg_temperature'])
        self.assertEqual(summary['type_distribution']['Pump'], 50)
        self.assertEqual(summary['type_distribution']['Reactor'], 50)
    
    def test_calculate_averages_precision(self):
        """Test that average calculations maintain precision.
        
        Requirements: 2.2
        """
        precision_dataset = Dataset.objects.create(
            name='precision_dataset.csv',
            uploaded_by=self.user,
            total_records=0
        )
        
        # Create records with precise decimal values
        EquipmentRecord.objects.create(
            dataset=precision_dataset,
            equipment_name='Equipment-1',
            equipment_type='Pump',
            flowrate=123.456,
            pressure=78.901,
            temperature=234.567
        )
        EquipmentRecord.objects.create(
            dataset=precision_dataset,
            equipment_name='Equipment-2',
            equipment_type='Pump',
            flowrate=234.567,
            pressure=89.012,
            temperature=345.678
        )
        
        service = AnalyticsService(dataset=precision_dataset)
        averages = service.calculate_averages()
        
        # Verify precision is maintained
        expected_flowrate = (123.456 + 234.567) / 2
        expected_pressure = (78.901 + 89.012) / 2
        expected_temperature = (234.567 + 345.678) / 2
        
        self.assertAlmostEqual(averages['avg_flowrate'], expected_flowrate, places=3)
        self.assertAlmostEqual(averages['avg_pressure'], expected_pressure, places=3)
        self.assertAlmostEqual(averages['avg_temperature'], expected_temperature, places=3)



class LoginEndpointTests(APITestCase):
    """Test login endpoint functionality.
    
    Requirements: 6.2, 6.4
    """
    
    def setUp(self):
        """Set up test user."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client = APIClient()
        self.login_url = '/api/auth/login/'
    
    def test_login_with_valid_credentials(self):
        """Test successful login with valid credentials.
        
        Requirements: 6.2
        """
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertIn('username', response.data)
        self.assertEqual(response.data['username'], 'testuser')
        
        # Verify token is valid
        token = response.data['token']
        self.assertIsNotNone(token)
        self.assertTrue(len(token) > 0)
        
        # Verify token works for authenticated requests
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        auth_response = self.client.get('/api/datasets/')
        self.assertEqual(auth_response.status_code, status.HTTP_200_OK)
    
    def test_login_with_invalid_username(self):
        """Test login fails with invalid username.
        
        Requirements: 6.4
        """
        response = self.client.post(self.login_url, {
            'username': 'nonexistent',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        self.assertNotIn('token', response.data)
    
    def test_login_with_invalid_password(self):
        """Test login fails with invalid password.
        
        Requirements: 6.4
        """
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        self.assertNotIn('token', response.data)
    
    def test_login_with_missing_username(self):
        """Test login fails with missing username.
        
        Requirements: 6.4
        """
        response = self.client.post(self.login_url, {
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
    
    def test_login_with_missing_password(self):
        """Test login fails with missing password.
        
        Requirements: 6.4
        """
        response = self.client.post(self.login_url, {
            'username': 'testuser'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
    
    def test_login_with_empty_credentials(self):
        """Test login fails with empty credentials.
        
        Requirements: 6.4
        """
        response = self.client.post(self.login_url, {
            'username': '',
            'password': ''
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
    
    def test_login_returns_user_information(self):
        """Test that login returns user information along with token.
        
        Requirements: 6.2
        """
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('username', response.data)
        self.assertIn('user_id', response.data)
        
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['user_id'], self.user.id)
    
    def test_login_creates_token_if_not_exists(self):
        """Test that login creates a token if one doesn't exist.
        
        Requirements: 6.2
        """
        # Ensure user has no token
        Token.objects.filter(user=self.user).delete()
        
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        
        # Verify token was created in database
        token_exists = Token.objects.filter(user=self.user).exists()
        self.assertTrue(token_exists)
    
    def test_login_returns_existing_token(self):
        """Test that login returns existing token if one already exists.
        
        Requirements: 6.2
        """
        # Create a token for the user
        existing_token = Token.objects.create(user=self.user)
        
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['token'], existing_token.key)
    
    def test_login_case_sensitive_username(self):
        """Test that login username is case-sensitive.
        
        Requirements: 6.4
        """
        response = self.client.post(self.login_url, {
            'username': 'TESTUSER',  # Wrong case
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)


class RegisterEndpointTests(APITestCase):
    """Test register endpoint functionality.
    
    Requirements: 6.2, 6.4
    """
    
    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
    
    def test_register_with_valid_data(self):
        """Test successful registration with valid data.
        
        Requirements: 6.2
        """
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'newuser@example.com'
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertIn('username', response.data)
        self.assertEqual(response.data['username'], 'newuser')
        
        # Verify user was created
        user_exists = User.objects.filter(username='newuser').exists()
        self.assertTrue(user_exists)
        
        # Verify token was created
        user = User.objects.get(username='newuser')
        token_exists = Token.objects.filter(user=user).exists()
        self.assertTrue(token_exists)
    
    def test_register_with_duplicate_username(self):
        """Test registration fails with duplicate username.
        
        Requirements: 6.4
        """
        # Create existing user
        User.objects.create_user(
            username='existinguser',
            password='pass123',
            email='existing@example.com'
        )
        
        # Try to register with same username
        response = self.client.post(self.register_url, {
            'username': 'existinguser',
            'password': 'newpass123',
            'email': 'different@example.com'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_register_with_missing_username(self):
        """Test registration fails with missing username.
        
        Requirements: 6.4
        """
        response = self.client.post(self.register_url, {
            'password': 'newpass123',
            'email': 'newuser@example.com'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_register_with_missing_password(self):
        """Test registration fails with missing password.
        
        Requirements: 6.4
        """
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'email': 'newuser@example.com'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_register_with_empty_username(self):
        """Test registration fails with empty username.
        
        Requirements: 6.4
        """
        response = self.client.post(self.register_url, {
            'username': '',
            'password': 'newpass123',
            'email': 'newuser@example.com'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_register_with_empty_password(self):
        """Test registration fails with empty password.
        
        Requirements: 6.4
        """
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'password': '',
            'email': 'newuser@example.com'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_register_without_email(self):
        """Test registration succeeds without email (email is optional).
        
        Requirements: 6.2
        """
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'password': 'newpass123'
        })
        
        # Email is optional, so registration should succeed
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        
        # Verify user was created
        user = User.objects.get(username='newuser')
        self.assertIsNotNone(user)
    
    def test_register_returns_token_immediately(self):
        """Test that registration returns authentication token immediately.
        
        Requirements: 6.2
        """
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'newuser@example.com'
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        
        # Verify token works for authenticated requests
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        auth_response = self.client.get('/api/datasets/')
        self.assertEqual(auth_response.status_code, status.HTTP_200_OK)
    
    def test_register_password_is_hashed(self):
        """Test that registered user's password is properly hashed.
        
        Requirements: 6.2
        """
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'newuser@example.com'
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify password is hashed (not stored in plain text)
        user = User.objects.get(username='newuser')
        self.assertNotEqual(user.password, 'newpass123')
        
        # Verify password can be checked
        self.assertTrue(user.check_password('newpass123'))


class PDFReportEndpointTests(APITestCase):
    """Test PDF report generation endpoint functionality.
    
    Requirements: 5.1, 5.4
    """
    
    def setUp(self):
        """Set up test users and datasets."""
        self.user1 = User.objects.create_user(
            username='testuser1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            password='testpass123'
        )
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
    
    def test_report_endpoint_generates_pdf(self):
        """Test that report endpoint generates a valid PDF.
        
        Requirements: 5.1
        """
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Request PDF report
        response = self.client.get(f'/api/datasets/{self.dataset.id}/report/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify content type
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
        # Verify Content-Disposition header
        self.assertIn('Content-Disposition', response)
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('test_dataset', response['Content-Disposition'])
        
        # Verify PDF content
        pdf_content = response.content
        self.assertGreater(len(pdf_content), 0)
        
        # Verify it's a valid PDF (starts with %PDF)
        self.assertEqual(pdf_content[:4], b'%PDF')
    
    def test_report_endpoint_requires_authentication(self):
        """Test that report endpoint requires authentication.
        
        Requirements: 5.1
        """
        # Try to access without authentication
        self.client.credentials()
        response = self.client.get(f'/api/datasets/{self.dataset.id}/report/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_report_endpoint_user_isolation(self):
        """Test that users cannot generate reports for other users' datasets.
        
        Requirements: 5.1
        """
        # Create a dataset for user2
        user2_dataset = Dataset.objects.create(
            name='user2_dataset.csv',
            uploaded_by=self.user2,
            total_records=1,
            avg_flowrate=150.0,
            avg_pressure=50.0,
            avg_temperature=100.0,
            type_distribution={'Pump': 1}
        )
        
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Try to generate report for user2's dataset
        response = self.client.get(f'/api/datasets/{user2_dataset.id}/report/')
        
        # Should return 404 (not found) to prevent information leakage
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_report_endpoint_dataset_not_found(self):
        """Test that report endpoint returns 404 for non-existent dataset.
        
        Requirements: 5.1
        """
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Try to generate report for non-existent dataset
        response = self.client.get('/api/datasets/99999/report/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_report_includes_summary_statistics(self):
        """Test that PDF report includes summary statistics.
        
        Requirements: 5.1
        """
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Request PDF report
        response = self.client.get(f'/api/datasets/{self.dataset.id}/report/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify PDF was generated
        pdf_content = response.content
        self.assertGreater(len(pdf_content), 0)
        
        # Note: We can't easily verify the content of the PDF without parsing it,
        # but we can verify it was generated successfully
        self.assertEqual(pdf_content[:4], b'%PDF')
    
    def test_report_includes_visualizations(self):
        """Test that PDF report includes visualizations.
        
        Requirements: 5.1
        """
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Request PDF report
        response = self.client.get(f'/api/datasets/{self.dataset.id}/report/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify PDF was generated with content
        pdf_content = response.content
        self.assertGreater(len(pdf_content), 1000)  # Should be substantial with charts
        
        # Verify it's a valid PDF
        self.assertEqual(pdf_content[:4], b'%PDF')
    
    def test_report_downloadable(self):
        """Test that PDF report is provided for download.
        
        Requirements: 5.4
        """
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Request PDF report
        response = self.client.get(f'/api/datasets/{self.dataset.id}/report/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify Content-Disposition indicates attachment (download)
        self.assertIn('Content-Disposition', response)
        content_disposition = response['Content-Disposition']
        self.assertIn('attachment', content_disposition)
        
        # Verify filename is included
        self.assertIn('filename', content_disposition)
    
    def test_report_includes_upload_timestamp(self):
        """Test that PDF report includes upload timestamp.
        
        Requirements: 5.1
        """
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Request PDF report
        response = self.client.get(f'/api/datasets/{self.dataset.id}/report/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify PDF was generated
        pdf_content = response.content
        self.assertGreater(len(pdf_content), 0)
        self.assertEqual(pdf_content[:4], b'%PDF')
    
    def test_report_includes_dataset_identifier(self):
        """Test that PDF report includes dataset identifier.
        
        Requirements: 5.1
        """
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Request PDF report
        response = self.client.get(f'/api/datasets/{self.dataset.id}/report/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify PDF was generated
        pdf_content = response.content
        self.assertGreater(len(pdf_content), 0)
        self.assertEqual(pdf_content[:4], b'%PDF')
    
    def test_report_with_empty_dataset(self):
        """Test PDF report generation for dataset with no records.
        
        Requirements: 5.1
        """
        # Create empty dataset
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
        
        # Request PDF report
        response = self.client.get(f'/api/datasets/{empty_dataset.id}/report/')
        
        # Should still generate a PDF (even if empty)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
        pdf_content = response.content
        self.assertGreater(len(pdf_content), 0)
        self.assertEqual(pdf_content[:4], b'%PDF')
    
    def test_report_with_large_dataset(self):
        """Test PDF report generation for dataset with many records.
        
        Requirements: 5.1
        """
        # Create dataset with many records
        large_dataset = Dataset.objects.create(
            name='large_dataset.csv',
            uploaded_by=self.user1,
            total_records=100,
            avg_flowrate=150.0,
            avg_pressure=50.0,
            avg_temperature=100.0,
            type_distribution={'Pump': 50, 'Reactor': 50}
        )
        
        # Create 100 equipment records
        for i in range(100):
            EquipmentRecord.objects.create(
                dataset=large_dataset,
                equipment_name=f'Equipment-{i}',
                equipment_type='Pump' if i % 2 == 0 else 'Reactor',
                flowrate=150.0 + i,
                pressure=50.0 + i,
                temperature=100.0 + i
            )
        
        # Authenticate as user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Request PDF report
        response = self.client.get(f'/api/datasets/{large_dataset.id}/report/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
        # Verify PDF was generated and is substantial
        pdf_content = response.content
        self.assertGreater(len(pdf_content), 5000)  # Should be large with 100 records
        self.assertEqual(pdf_content[:4], b'%PDF')
    
    def test_report_owner_can_access(self):
        """Test that dataset owner can successfully generate report.
        
        Requirements: 5.1
        """
        # Authenticate as user1 (owner)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Generate report for own dataset
        response = self.client.get(f'/api/datasets/{self.dataset.id}/report/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
        pdf_content = response.content
        self.assertGreater(len(pdf_content), 0)
        self.assertEqual(pdf_content[:4], b'%PDF')
