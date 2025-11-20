"""
CSV Processing Service for Chemical Equipment Analytics.

This module provides CSV validation and parsing functionality for equipment data files.
"""

import pandas as pd
from typing import Dict, List, Tuple, Any


class CSVValidationError(Exception):
    """Custom exception for CSV validation errors."""
    pass


class CSVProcessor:
    """
    Service class for processing and validating CSV files containing equipment data.
    
    This class handles:
    - CSV structure validation
    - Required column verification
    - Data type validation for numeric fields
    - Data parsing and extraction
    """
    
    # Required columns in the CSV file
    REQUIRED_COLUMNS = [
        'Equipment Name',
        'Type',
        'Flowrate',
        'Pressure',
        'Temperature'
    ]
    
    # Numeric columns that need validation
    NUMERIC_COLUMNS = ['Flowrate', 'Pressure', 'Temperature']
    
    def __init__(self):
        """Initialize the CSVProcessor."""
        pass
    
    def validate_csv_structure(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate that the CSV has all required columns.
        
        Args:
            df: Pandas DataFrame containing the CSV data
            
        Returns:
            Tuple of (is_valid, missing_columns)
            - is_valid: Boolean indicating if structure is valid
            - missing_columns: List of missing column names
        """
        # Get the actual columns from the DataFrame
        actual_columns = set(df.columns)
        required_columns = set(self.REQUIRED_COLUMNS)
        
        # Find missing columns
        missing_columns = list(required_columns - actual_columns)
        
        is_valid = len(missing_columns) == 0
        
        return is_valid, missing_columns
    
    def validate_numeric_fields(self, df: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate that numeric columns contain valid numeric data.
        
        Args:
            df: Pandas DataFrame containing the CSV data
            
        Returns:
            Tuple of (is_valid, errors)
            - is_valid: Boolean indicating if all numeric fields are valid
            - errors: Dictionary containing validation error details
        """
        errors = {}
        
        for column in self.NUMERIC_COLUMNS:
            if column not in df.columns:
                continue
                
            # Check if column can be converted to numeric
            try:
                # Attempt to convert to numeric, coerce errors to NaN
                numeric_series = pd.to_numeric(df[column], errors='coerce')
                
                # Check for NaN values (invalid conversions)
                invalid_count = numeric_series.isna().sum()
                original_na_count = df[column].isna().sum()
                
                # If we have more NaN after conversion, some values were invalid
                if invalid_count > original_na_count:
                    invalid_indices = numeric_series.isna() & ~df[column].isna()
                    invalid_values = df.loc[invalid_indices, column].tolist()
                    
                    errors[column] = {
                        'message': f'Column contains non-numeric values',
                        'invalid_count': invalid_count - original_na_count,
                        'sample_invalid_values': invalid_values[:5]  # Show first 5 invalid values
                    }
                
                # Check for non-positive values in Flowrate and Pressure (must be positive, > 0)
                if column in ['Flowrate', 'Pressure']:
                    non_positive_values = numeric_series[numeric_series <= 0]
                    if len(non_positive_values) > 0:
                        if column not in errors:
                            errors[column] = {}
                        errors[column]['non_positive_values'] = {
                            'message': f'{column} must be positive (greater than 0)',
                            'count': len(non_positive_values),
                            'sample_values': non_positive_values.head(5).tolist()
                        }
                        
            except Exception as e:
                errors[column] = {
                    'message': f'Error validating column: {str(e)}'
                }
        
        is_valid = len(errors) == 0
        
        return is_valid, errors
    
    def validate_required_fields(self, df: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate that required fields are not empty.
        
        Args:
            df: Pandas DataFrame containing the CSV data
            
        Returns:
            Tuple of (is_valid, errors)
            - is_valid: Boolean indicating if all required fields have values
            - errors: Dictionary containing validation error details
        """
        errors = {}
        
        for column in self.REQUIRED_COLUMNS:
            if column not in df.columns:
                continue
            
            # Check for empty/null values
            null_count = df[column].isna().sum()
            empty_count = (df[column].astype(str).str.strip() == '').sum()
            
            total_empty = null_count + empty_count
            
            if total_empty > 0:
                errors[column] = {
                    'message': f'Column contains empty values',
                    'empty_count': total_empty,
                    'total_rows': len(df)
                }
        
        is_valid = len(errors) == 0
        
        return is_valid, errors
    
    def validate(self, file_path: str = None, file_content: Any = None) -> Dict[str, Any]:
        """
        Validate a CSV file completely.
        
        Args:
            file_path: Path to the CSV file (optional)
            file_content: File-like object or content (optional)
            
        Returns:
            Dictionary containing validation results:
            {
                'is_valid': bool,
                'errors': dict,
                'dataframe': pd.DataFrame (if valid)
            }
            
        Raises:
            CSVValidationError: If the file cannot be read or parsed
        """
        try:
            # Read the CSV file
            if file_path:
                df = pd.read_csv(file_path)
            elif file_content:
                df = pd.read_csv(file_content)
            else:
                raise CSVValidationError("Either file_path or file_content must be provided")
            
            # Check if DataFrame is empty
            if df.empty:
                raise CSVValidationError("CSV file is empty")
            
            validation_result = {
                'is_valid': True,
                'errors': {},
                'dataframe': None
            }
            
            # Validate structure (required columns)
            structure_valid, missing_columns = self.validate_csv_structure(df)
            if not structure_valid:
                validation_result['is_valid'] = False
                validation_result['errors']['missing_columns'] = {
                    'message': 'CSV is missing required columns',
                    'missing': missing_columns,
                    'required': self.REQUIRED_COLUMNS
                }
                # Return early if structure is invalid
                return validation_result
            
            # Validate required fields are not empty
            fields_valid, field_errors = self.validate_required_fields(df)
            if not fields_valid:
                validation_result['is_valid'] = False
                validation_result['errors']['empty_fields'] = field_errors
            
            # Validate numeric fields
            numeric_valid, numeric_errors = self.validate_numeric_fields(df)
            if not numeric_valid:
                validation_result['is_valid'] = False
                validation_result['errors']['numeric_validation'] = numeric_errors
            
            # If all validations passed, include the dataframe
            if validation_result['is_valid']:
                validation_result['dataframe'] = df
            
            return validation_result
            
        except pd.errors.EmptyDataError:
            raise CSVValidationError("CSV file is empty or has no data")
        except pd.errors.ParserError as e:
            raise CSVValidationError(f"Error parsing CSV file: {str(e)}")
        except Exception as e:
            raise CSVValidationError(f"Error reading CSV file: {str(e)}")
    
    def parse_to_records(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Parse a validated DataFrame into a list of equipment record dictionaries.
        
        Args:
            df: Validated Pandas DataFrame
            
        Returns:
            List of dictionaries, each representing an equipment record
        """
        records = []
        
        for _, row in df.iterrows():
            record = {
                'equipment_name': str(row['Equipment Name']).strip(),
                'equipment_type': str(row['Type']).strip(),
                'flowrate': float(row['Flowrate']),
                'pressure': float(row['Pressure']),
                'temperature': float(row['Temperature'])
            }
            records.append(record)
        
        return records
    
    def parse_csv_file(self, file_content: Any) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
        """
        Parse a CSV file using Pandas and convert to equipment records.
        
        This method:
        1. Reads the CSV file using Pandas
        2. Validates the structure and data
        3. Converts the DataFrame to a list of record dictionaries
        
        Args:
            file_content: File-like object containing CSV data
            
        Returns:
            Tuple of (dataframe, records_list)
            - dataframe: The validated Pandas DataFrame
            - records_list: List of dictionaries ready for model creation
            
        Raises:
            CSVValidationError: If validation fails or parsing encounters errors
        """
        try:
            # Validate the CSV file
            validation_result = self.validate(file_content=file_content)
            
            if not validation_result['is_valid']:
                # Build a detailed error message
                error_messages = []
                for error_type, error_details in validation_result['errors'].items():
                    if error_type == 'missing_columns':
                        missing = ', '.join(error_details['missing'])
                        error_messages.append(f"Missing required columns: {missing}")
                    elif error_type == 'empty_fields':
                        for field, details in error_details.items():
                            error_messages.append(
                                f"{field}: {details['empty_count']} empty values out of {details['total_rows']} rows"
                            )
                    elif error_type == 'numeric_validation':
                        for field, details in error_details.items():
                            if 'message' in details:
                                error_messages.append(f"{field}: {details['message']}")
                            if 'non_positive_values' in details:
                                error_messages.append(
                                    f"{field}: {details['non_positive_values']['message']} "
                                    f"({details['non_positive_values']['count']} invalid values found)"
                                )
                
                raise CSVValidationError('; '.join(error_messages))
            
            # Get the validated DataFrame
            df = validation_result['dataframe']
            
            # Convert DataFrame to record dictionaries
            records = self.parse_to_records(df)
            
            return df, records
            
        except CSVValidationError:
            # Re-raise validation errors as-is
            raise
        except Exception as e:
            # Wrap any other exceptions
            raise CSVValidationError(f"Error parsing CSV file: {str(e)}")
    
    def create_equipment_records(self, dataset, records_data: List[Dict[str, Any]]):
        """
        Create EquipmentRecord model instances from parsed data.
        
        This method takes a list of record dictionaries and creates
        EquipmentRecord instances associated with the given dataset.
        Uses bulk_create for efficient database insertion.
        
        Args:
            dataset: Dataset model instance to associate records with
            records_data: List of dictionaries containing equipment record data
            
        Returns:
            List of created EquipmentRecord instances
            
        Raises:
            Exception: If database operations fail
        """
        from ..models import EquipmentRecord
        
        try:
            # Create EquipmentRecord instances (not yet saved to DB)
            equipment_records = [
                EquipmentRecord(
                    dataset=dataset,
                    equipment_name=record['equipment_name'],
                    equipment_type=record['equipment_type'],
                    flowrate=record['flowrate'],
                    pressure=record['pressure'],
                    temperature=record['temperature']
                )
                for record in records_data
            ]
            
            # Bulk create all records in a single database operation
            created_records = EquipmentRecord.objects.bulk_create(equipment_records)
            
            return created_records
            
        except Exception as e:
            raise Exception(f"Error creating equipment records: {str(e)}")
