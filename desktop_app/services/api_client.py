"""
API Client for Chemical Equipment Analytics Desktop Application.

This module provides a comprehensive API client for communicating with the
Django REST API backend. It handles authentication, token storage, and all
API endpoint interactions.

Requirements: 1.2, 2.5, 4.4, 5.2
"""

import requests
import json
import os
from typing import Dict, List, Optional, Any, BinaryIO
from pathlib import Path


class APIClientError(Exception):
    """Base exception for API client errors."""
    pass


class AuthenticationError(APIClientError):
    """Raised when authentication fails."""
    pass


class NetworkError(APIClientError):
    """Raised when network communication fails."""
    pass


class ValidationError(APIClientError):
    """Raised when request validation fails."""
    pass


class APIClient:
    """
    API client for communicating with the Django REST API backend.
    
    This client handles:
    - Authentication and token management
    - All API endpoint interactions
    - Error handling and network issues
    - Token persistence across sessions
    
    Attributes:
        base_url (str): Base URL of the API server
        token (str): Authentication token
        timeout (int): Request timeout in seconds
    """
    
    def __init__(self, base_url: str = "http://localhost:8000/api", timeout: int = 30):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the API server (default: http://localhost:8000/api)
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url.rstrip('/')
        self.token: Optional[str] = None
        self.timeout = timeout
        self._token_file = Path.home() / '.chemical_equipment_analytics' / 'token.txt'
        
        # Load saved token if available
        self._load_token()
    
    def _get_headers(self, include_auth: bool = True) -> Dict[str, str]:
        """
        Get HTTP headers for API requests.
        
        Args:
            include_auth: Whether to include authentication token
            
        Returns:
            Dictionary of HTTP headers
        """
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if include_auth and self.token:
            headers['Authorization'] = f'Token {self.token}'
        
        return headers
    
    def _handle_response(self, response: requests.Response) -> Any:
        """
        Handle API response and raise appropriate exceptions.
        
        Args:
            response: Response object from requests
            
        Returns:
            Parsed JSON response data
            
        Raises:
            AuthenticationError: If authentication fails (401)
            ValidationError: If request validation fails (400)
            APIClientError: For other API errors
        """
        try:
            # Check for successful response
            if response.status_code in [200, 201]:
                return response.json() if response.content else {}
            
            # Handle error responses
            error_data = response.json() if response.content else {}
            error_message = error_data.get('message') or error_data.get('error') or response.text
            
            if response.status_code == 401:
                raise AuthenticationError(f"Authentication failed: {error_message}")
            elif response.status_code == 400:
                raise ValidationError(f"Validation error: {error_message}")
            elif response.status_code == 404:
                raise APIClientError(f"Resource not found: {error_message}")
            elif response.status_code >= 500:
                raise APIClientError(f"Server error: {error_message}")
            else:
                raise APIClientError(f"API error ({response.status_code}): {error_message}")
                
        except requests.exceptions.JSONDecodeError:
            raise APIClientError(f"Invalid JSON response: {response.text}")
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        params: Optional[Dict] = None,
        include_auth: bool = True
    ) -> Any:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data (for JSON requests)
            files: Files to upload (for multipart requests)
            params: Query parameters
            include_auth: Whether to include authentication token
            
        Returns:
            Parsed response data
            
        Raises:
            NetworkError: If network communication fails
            APIClientError: For API errors
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            # Prepare headers
            headers = self._get_headers(include_auth=include_auth)
            
            # For file uploads, don't set Content-Type (let requests handle it)
            if files:
                headers.pop('Content-Type', None)
            
            # Make the request
            response = requests.request(
                method=method,
                url=url,
                json=data if not files else None,
                files=files,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            
            return self._handle_response(response)
            
        except requests.exceptions.Timeout:
            raise NetworkError(f"Request timed out after {self.timeout} seconds")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {str(e)}")
    
    def _save_token(self):
        """Save authentication token to file."""
        if self.token:
            try:
                self._token_file.parent.mkdir(parents=True, exist_ok=True)
                self._token_file.write_text(self.token)
            except Exception as e:
                # Non-critical error, just log it
                print(f"Warning: Could not save token: {e}")
    
    def _load_token(self):
        """Load authentication token from file."""
        try:
            if self._token_file.exists():
                self.token = self._token_file.read_text().strip()
        except Exception as e:
            # Non-critical error, just log it
            print(f"Warning: Could not load token: {e}")
    
    def _clear_token(self):
        """Clear authentication token from memory and file."""
        self.token = None
        try:
            if self._token_file.exists():
                self._token_file.unlink()
        except Exception as e:
            print(f"Warning: Could not delete token file: {e}")
    
    # Authentication Methods
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and obtain authentication token.
        
        Args:
            username: User's username
            password: User's password
            
        Returns:
            Dictionary containing token, user_id, and username
            
        Raises:
            AuthenticationError: If credentials are invalid
            NetworkError: If network communication fails
            
        Requirements: 6.3, 6.4
        """
        data = {
            'username': username,
            'password': password
        }
        
        response = self._make_request(
            method='POST',
            endpoint='auth/login/',
            data=data,
            include_auth=False
        )
        
        # Store the token
        self.token = response.get('token')
        self._save_token()
        
        return response
    
    def register(self, username: str, password: str, email: str = '') -> Dict[str, Any]:
        """
        Register a new user account.
        
        Args:
            username: Desired username
            password: Desired password
            email: User's email address (optional)
            
        Returns:
            Dictionary containing token, user_id, and username
            
        Raises:
            ValidationError: If registration data is invalid
            NetworkError: If network communication fails
        """
        data = {
            'username': username,
            'password': password,
            'email': email
        }
        
        response = self._make_request(
            method='POST',
            endpoint='auth/register/',
            data=data,
            include_auth=False
        )
        
        # Store the token
        self.token = response.get('token')
        self._save_token()
        
        return response
    
    def logout(self) -> Dict[str, Any]:
        """
        Logout the current user and invalidate token.
        
        Returns:
            Dictionary with logout confirmation message
            
        Raises:
            AuthenticationError: If not authenticated
            NetworkError: If network communication fails
        """
        response = self._make_request(
            method='POST',
            endpoint='auth/logout/',
            include_auth=True
        )
        
        # Clear the token
        self._clear_token()
        
        return response
    
    def is_authenticated(self) -> bool:
        """
        Check if the client has an authentication token.
        
        Returns:
            True if authenticated, False otherwise
        """
        return self.token is not None
    
    # Dataset Management Methods
    
    def upload_dataset(self, file_path: str) -> Dict[str, Any]:
        """
        Upload a CSV file containing equipment data.
        
        Args:
            file_path: Path to the CSV file to upload
            
        Returns:
            Dictionary containing the created dataset information
            
        Raises:
            ValidationError: If CSV validation fails
            NetworkError: If network communication fails
            FileNotFoundError: If file doesn't exist
            
        Requirements: 1.2, 1.3, 1.4
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'rb') as f:
            files = {
                'file': (os.path.basename(file_path), f, 'text/csv')
            }
            
            response = self._make_request(
                method='POST',
                endpoint='datasets/upload/',
                files=files,
                include_auth=True
            )
        
        return response
    
    def get_datasets(self) -> List[Dict[str, Any]]:
        """
        Get list of datasets (last 5).
        
        Returns:
            List of dataset dictionaries with summary information
            
        Raises:
            AuthenticationError: If not authenticated
            NetworkError: If network communication fails
            
        Requirements: 4.4
        """
        response = self._make_request(
            method='GET',
            endpoint='datasets/',
            include_auth=True
        )
        
        return response
    
    def get_dataset(self, dataset_id: int) -> Dict[str, Any]:
        """
        Get details for a specific dataset.
        
        Args:
            dataset_id: ID of the dataset to retrieve
            
        Returns:
            Dictionary containing dataset details
            
        Raises:
            AuthenticationError: If not authenticated
            APIClientError: If dataset not found
            NetworkError: If network communication fails
            
        Requirements: 4.5
        """
        response = self._make_request(
            method='GET',
            endpoint=f'datasets/{dataset_id}/',
            include_auth=True
        )
        
        return response
    
    def get_dataset_data(
        self,
        dataset_id: int,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        Get equipment records for a specific dataset with pagination.
        
        Args:
            dataset_id: ID of the dataset
            page: Page number (default: 1)
            page_size: Number of records per page (default: 50)
            
        Returns:
            Dictionary containing paginated equipment records with keys:
            - count: Total number of records
            - next: URL for next page (or None)
            - previous: URL for previous page (or None)
            - results: List of equipment record dictionaries
            
        Raises:
            AuthenticationError: If not authenticated
            APIClientError: If dataset not found
            NetworkError: If network communication fails
            
        Requirements: 4.5
        """
        params = {
            'page': page,
            'page_size': page_size
        }
        
        response = self._make_request(
            method='GET',
            endpoint=f'datasets/{dataset_id}/data/',
            params=params,
            include_auth=True
        )
        
        return response
    
    def get_dataset_summary(self, dataset_id: int) -> Dict[str, Any]:
        """
        Get summary statistics for a specific dataset.
        
        Args:
            dataset_id: ID of the dataset
            
        Returns:
            Dictionary containing summary statistics:
            - id: Dataset ID
            - name: Dataset name
            - uploaded_at: Upload timestamp
            - total_records: Total number of equipment records
            - avg_flowrate: Average flowrate
            - avg_pressure: Average pressure
            - avg_temperature: Average temperature
            - type_distribution: Dictionary of equipment type counts
            
        Raises:
            AuthenticationError: If not authenticated
            APIClientError: If dataset not found
            NetworkError: If network communication fails
            
        Requirements: 2.5
        """
        response = self._make_request(
            method='GET',
            endpoint=f'datasets/{dataset_id}/summary/',
            include_auth=True
        )
        
        return response
    
    def delete_dataset(self, dataset_id: int) -> None:
        """
        Delete a specific dataset.
        
        Args:
            dataset_id: ID of the dataset to delete
            
        Raises:
            AuthenticationError: If not authenticated
            APIClientError: If dataset not found or deletion fails
            NetworkError: If network communication fails
        """
        self._make_request(
            method='DELETE',
            endpoint=f'datasets/{dataset_id}//',
            include_auth=True
        )
    
    # Report Generation Methods
    
    def download_report(self, dataset_id: int, save_path: str) -> str:
        """
        Generate and download a PDF report for a specific dataset.
        
        Args:
            dataset_id: ID of the dataset
            save_path: Path where the PDF file should be saved
            
        Returns:
            Path to the saved PDF file
            
        Raises:
            AuthenticationError: If not authenticated
            APIClientError: If dataset not found or report generation fails
            NetworkError: If network communication fails
            
        Requirements: 5.2, 5.4
        """
        url = f"{self.base_url}/datasets/{dataset_id}/report/"
        
        try:
            headers = self._get_headers(include_auth=True)
            
            # Make request to get PDF
            response = requests.get(
                url,
                headers=headers,
                timeout=self.timeout,
                stream=True
            )
            
            # Check for errors
            if response.status_code != 200:
                error_message = response.text
                if response.status_code == 401:
                    raise AuthenticationError(f"Authentication failed: {error_message}")
                elif response.status_code == 404:
                    raise APIClientError(f"Dataset not found: {error_message}")
                else:
                    raise APIClientError(f"Report generation failed: {error_message}")
            
            # Save PDF to file
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return save_path
            
        except requests.exceptions.Timeout:
            raise NetworkError(f"Request timed out after {self.timeout} seconds")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {str(e)}")
        except IOError as e:
            raise APIClientError(f"Failed to save PDF file: {str(e)}")
    
    # Utility Methods
    
    def set_base_url(self, base_url: str):
        """
        Update the base URL for the API.
        
        Args:
            base_url: New base URL
        """
        self.base_url = base_url.rstrip('/')
    
    def set_timeout(self, timeout: int):
        """
        Update the request timeout.
        
        Args:
            timeout: New timeout in seconds
        """
        self.timeout = timeout
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Check if the API server is reachable.
        
        Returns:
            Dictionary with connection status information:
            - connected: Boolean indicating if server is reachable
            - message: Status message
        """
        try:
            response = requests.get(
                f"{self.base_url}/",
                timeout=5
            )
            return {
                'connected': True,
                'message': 'API server is reachable',
                'status_code': response.status_code
            }
        except requests.exceptions.RequestException as e:
            return {
                'connected': False,
                'message': f'Cannot reach API server: {str(e)}',
                'status_code': None
            }
