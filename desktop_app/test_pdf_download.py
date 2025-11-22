"""
Test script for PDF download functionality in MainWindow.

This script tests the PDF download logic implementation for task 22.2.

Requirements: 5.2, 5.4
"""

import sys
import os
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.main_window import MainWindow
from services.api_client import APIClient


def test_pdf_download_no_dataset(app):
    """Test PDF download when no dataset is loaded."""
    print("Test 1: PDF download with no dataset loaded")
    
    # Create mock API client
    api_client = Mock(spec=APIClient)
    
    # Create main window
    window = MainWindow(api_client)
    window.current_dataset = None
    
    # Mock show_info to capture the call
    with patch.object(window, 'show_info') as mock_show_info:
        # Trigger report action
        window._handle_report_action()
        
        # Verify show_info was called with appropriate message
        mock_show_info.assert_called_once()
        args = mock_show_info.call_args[0]
        assert "No Dataset" in args[0]
        print("✓ Correctly shows info dialog when no dataset is loaded")


def test_pdf_download_invalid_dataset(app):
    """Test PDF download with invalid dataset (no ID)."""
    print("\nTest 2: PDF download with invalid dataset")
    
    # Create mock API client
    api_client = Mock(spec=APIClient)
    
    # Create main window
    window = MainWindow(api_client)
    window.current_dataset = {'name': 'test.csv'}  # No ID
    
    # Mock show_error to capture the call
    with patch.object(window, 'show_error') as mock_show_error:
        # Trigger report action
        window._handle_report_action()
        
        # Verify show_error was called
        mock_show_error.assert_called_once()
        args = mock_show_error.call_args[0]
        assert "Error" in args[0]
        assert "Invalid dataset" in args[1]
        print("✓ Correctly shows error dialog for invalid dataset")


def test_pdf_download_user_cancels(app):
    """Test PDF download when user cancels file dialog."""
    print("\nTest 3: PDF download when user cancels file dialog")
    
    # Create mock API client
    api_client = Mock(spec=APIClient)
    
    # Create main window
    window = MainWindow(api_client)
    window.current_dataset = {'id': 1, 'name': 'test.csv'}
    
    # Mock QFileDialog to return empty path (user cancelled)
    with patch('ui.main_window.QFileDialog.getSaveFileName') as mock_dialog:
        mock_dialog.return_value = ('', '')  # User cancelled
        
        # Mock show_info to ensure it's not called
        with patch.object(window, 'show_info') as mock_show_info:
            # Trigger report action
            window._handle_report_action()
            
            # Verify show_info was not called (function returned early)
            mock_show_info.assert_not_called()
            print("✓ Correctly handles user cancellation")


def test_pdf_download_success(app):
    """Test successful PDF download."""
    print("\nTest 4: Successful PDF download")
    
    # Create mock API client
    api_client = Mock(spec=APIClient)
    api_client.download_report = Mock(return_value='/tmp/test_report.pdf')
    
    # Create main window
    window = MainWindow(api_client)
    window.current_dataset = {'id': 1, 'name': 'test_data.csv'}
    
    # Mock QFileDialog to return a save path
    with patch('ui.main_window.QFileDialog.getSaveFileName') as mock_dialog:
        mock_dialog.return_value = ('/tmp/test_report.pdf', 'PDF Files (*.pdf)')
        
        # Mock QProgressDialog to avoid showing it
        with patch('ui.main_window.QProgressDialog') as MockProgressDialog:
            mock_progress_instance = MagicMock()
            MockProgressDialog.return_value = mock_progress_instance
            
            # Mock show_info to capture success message
            with patch.object(window, 'show_info') as mock_show_info:
                # Trigger report action
                window._handle_report_action()
                
                # Verify API client was called with correct parameters
                api_client.download_report.assert_called_once_with(1, '/tmp/test_report.pdf')
                
                # Verify progress dialog was created and closed
                MockProgressDialog.assert_called_once()
                mock_progress_instance.close.assert_called()
                
                # Verify success message was shown
                mock_show_info.assert_called_once()
                args = mock_show_info.call_args[0]
                assert "Report Generated" in args[0]
                assert "/tmp/test_report.pdf" in args[1]
                print("✓ Successfully downloads PDF and shows success message")


def test_pdf_download_api_error(app):
    """Test PDF download when API returns an error."""
    print("\nTest 5: PDF download with API error")
    
    # Create mock API client that raises an exception
    api_client = Mock(spec=APIClient)
    api_client.download_report = Mock(side_effect=Exception("Network error"))
    
    # Create main window
    window = MainWindow(api_client)
    window.current_dataset = {'id': 1, 'name': 'test_data.csv'}
    
    # Mock QFileDialog to return a save path
    with patch('ui.main_window.QFileDialog.getSaveFileName') as mock_dialog:
        mock_dialog.return_value = ('/tmp/test_report.pdf', 'PDF Files (*.pdf)')
        
        # Mock QProgressDialog
        with patch('ui.main_window.QProgressDialog') as MockProgressDialog:
            mock_progress_instance = MagicMock()
            MockProgressDialog.return_value = mock_progress_instance
            
            # Mock show_error to capture error message
            with patch.object(window, 'show_error') as mock_show_error:
                # Trigger report action
                window._handle_report_action()
                
                # Verify progress dialog was closed
                mock_progress_instance.close.assert_called()
                
                # Verify error message was shown
                mock_show_error.assert_called_once()
                args = mock_show_error.call_args[0]
                assert "Report Generation Failed" in args[0]
                assert "Network error" in args[1]
                print("✓ Correctly handles API errors and shows error message")


def test_pdf_download_filename_handling(app):
    """Test that filename is properly formatted."""
    print("\nTest 6: PDF filename handling")
    
    # Create mock API client
    api_client = Mock(spec=APIClient)
    api_client.download_report = Mock(return_value='/tmp/equipment_data_report.pdf')
    
    # Create main window
    window = MainWindow(api_client)
    window.current_dataset = {'id': 1, 'name': 'equipment_data.csv'}
    
    # Mock QFileDialog to capture the default filename
    with patch('ui.main_window.QFileDialog.getSaveFileName') as mock_dialog:
        mock_dialog.return_value = ('/tmp/equipment_data_report.pdf', 'PDF Files (*.pdf)')
        
        # Mock QProgressDialog
        with patch('ui.main_window.QProgressDialog') as MockProgressDialog:
            mock_progress_instance = MagicMock()
            MockProgressDialog.return_value = mock_progress_instance
            
            # Mock show_info
            with patch.object(window, 'show_info'):
                # Trigger report action
                window._handle_report_action()
                
                # Verify QFileDialog was called with correct default filename
                # getSaveFileName is called with: (parent, caption, directory, filter)
                call_args = mock_dialog.call_args
                # The third argument (index 2) is the default filename/directory
                default_filename = call_args[0][2] if len(call_args[0]) > 2 else call_args[1].get('directory', '')
                assert default_filename == "equipment_data_report.pdf", f"Expected 'equipment_data_report.pdf', got '{default_filename}'"
                print("✓ Correctly formats default filename (removes .csv, adds _report.pdf)")


def test_pdf_download_adds_extension(app):
    """Test that .pdf extension is added if missing."""
    print("\nTest 7: PDF extension handling")
    
    # Create mock API client
    api_client = Mock(spec=APIClient)
    api_client.download_report = Mock(return_value='/tmp/report.pdf')
    
    # Create main window
    window = MainWindow(api_client)
    window.current_dataset = {'id': 1, 'name': 'test.csv'}
    
    # Mock QFileDialog to return path without .pdf extension
    with patch('ui.main_window.QFileDialog.getSaveFileName') as mock_dialog:
        mock_dialog.return_value = ('/tmp/report', 'PDF Files (*.pdf)')
        
        # Mock QProgressDialog
        with patch('ui.main_window.QProgressDialog') as MockProgressDialog:
            mock_progress_instance = MagicMock()
            MockProgressDialog.return_value = mock_progress_instance
            
            # Mock show_info
            with patch.object(window, 'show_info'):
                # Trigger report action
                window._handle_report_action()
                
                # Verify API client was called with .pdf extension added
                call_args = api_client.download_report.call_args[0]
                save_path = call_args[1]
                assert save_path == '/tmp/report.pdf'
                print("✓ Correctly adds .pdf extension if missing")


if __name__ == '__main__':
    print("=" * 60)
    print("Testing PDF Download Functionality (Task 22.2)")
    print("=" * 60)
    
    # Create single QApplication instance for all tests
    app = QApplication(sys.argv)
    
    try:
        test_pdf_download_no_dataset(app)
        test_pdf_download_invalid_dataset(app)
        test_pdf_download_user_cancels(app)
        test_pdf_download_success(app)
        test_pdf_download_api_error(app)
        test_pdf_download_filename_handling(app)
        test_pdf_download_adds_extension(app)
        
        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        app.quit()
