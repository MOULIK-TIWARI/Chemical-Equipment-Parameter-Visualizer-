"""
Complete workflow test for PyQt5 desktop application (Task 27.2).

This script tests the entire workflow:
1. Login flow
2. CSV upload with sample data
3. Dashboard display verification
4. History navigation
5. PDF download

Requirements: All
"""

import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from ui.main_window import MainWindow
from ui.login_dialog import LoginDialog
from services.api_client import APIClient
from utils.config import get_config


class WorkflowTestResults:
    """Track workflow test results."""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def add_pass(self, test_name):
        self.passed += 1
        self.tests.append((test_name, True, None))
        print(f"  ✓ {test_name}")
    
    def add_fail(self, test_name, error=None):
        self.failed += 1
        self.tests.append((test_name, False, error))
        print(f"  ✗ {test_name}")
        if error:
            print(f"    Error: {error}")

    def summary(self):
        total = self.passed + self.failed
        print(f"\nTotal: {total} tests, {self.passed} passed, {self.failed} failed")
        return self.failed == 0


def test_login_flow():
    """Test 1: Login flow."""
    print("\n" + "=" * 60)
    print("Test 1: Login Flow")
    print("=" * 60)
    
    results = WorkflowTestResults()
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Test LoginDialog creation
    try:
        config = get_config()
        api_client = APIClient(base_url=config.api_base_url)
        dialog = LoginDialog(api_client)
        results.add_pass("LoginDialog instantiation")
    except Exception as e:
        results.add_fail("LoginDialog instantiation", str(e))
        return results
    
    # Test dialog has required fields
    try:
        assert hasattr(dialog, 'username_input'), "Missing username_input"
        assert hasattr(dialog, 'password_input'), "Missing password_input"
        assert hasattr(dialog, 'login_button'), "Missing login_button"
        results.add_pass("Login dialog has required fields")
    except AssertionError as e:
        results.add_fail("Login dialog has required fields", str(e))
    
    # Test login signal exists
    try:
        assert hasattr(dialog, 'login_successful'), "Missing login_successful signal"
        results.add_pass("Login successful signal exists")
    except AssertionError as e:
        results.add_fail("Login successful signal exists", str(e))

    # Test form validation
    try:
        dialog.username_input.setText("")
        dialog.password_input.setText("")
        is_valid = dialog._validate_form()
        assert not is_valid, "Empty form should not be valid"
        results.add_pass("Form validation rejects empty fields")
    except Exception as e:
        results.add_fail("Form validation rejects empty fields", str(e))
    
    # Test valid form
    try:
        dialog.username_input.setText("testuser")
        dialog.password_input.setText("testpass123")
        is_valid = dialog._validate_form()
        assert is_valid, "Valid form should pass validation"
        results.add_pass("Form validation accepts valid input")
    except Exception as e:
        results.add_fail("Form validation accepts valid input", str(e))
    
    # Test mock login
    try:
        with patch.object(api_client, 'login') as mock_login:
            mock_login.return_value = {
                'token': 'test_token_123',
                'username': 'testuser',
                'user_id': 1
            }
            
            signal_received = []
            dialog.login_successful.connect(lambda x: signal_received.append(x))
            
            dialog.username_input.setText("testuser")
            dialog.password_input.setText("testpass123")
            dialog._handle_login()
            
            assert len(signal_received) == 1, "Login signal should be emitted"
            assert signal_received[0]['username'] == 'testuser'
            results.add_pass("Login flow completes successfully")
    except Exception as e:
        results.add_fail("Login flow completes successfully", str(e))
    
    return results



def test_csv_upload():
    """Test 2: CSV upload with sample data."""
    print("\n" + "=" * 60)
    print("Test 2: CSV Upload with Sample Data")
    print("=" * 60)
    
    results = WorkflowTestResults()
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Create main window
    try:
        config = get_config()
        api_client = APIClient(base_url=config.api_base_url)
        user_info = {'username': 'testuser', 'user_id': 1, 'token': 'test_token'}
        main_window = MainWindow(api_client, user_info)
        results.add_pass("Main window creation")
    except Exception as e:
        results.add_fail("Main window creation", str(e))
        return results
    
    # Test upload widget exists
    try:
        assert hasattr(main_window, 'upload_widget'), "Missing upload_widget"
        assert main_window.upload_widget is not None
        results.add_pass("Upload widget exists in main window")
    except AssertionError as e:
        results.add_fail("Upload widget exists in main window", str(e))
    
    # Test upload widget is first tab
    try:
        first_tab = main_window.tab_widget.widget(0)
        assert first_tab is main_window.upload_widget
        tab_text = main_window.tab_widget.tabText(0)
        assert tab_text == "Upload"
        results.add_pass("Upload widget is first tab")
    except AssertionError as e:
        results.add_fail("Upload widget is first tab", str(e))

    # Test sample CSV file exists
    try:
        sample_csv_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'sample_equipment_data.csv')
        assert os.path.exists(sample_csv_path), f"Sample CSV not found at {sample_csv_path}"
        results.add_pass("Sample CSV file exists")
    except AssertionError as e:
        results.add_fail("Sample CSV file exists", str(e))
    
    # Test upload functionality with mock
    try:
        with patch.object(api_client, 'upload_dataset') as mock_upload:
            mock_upload.return_value = {
                'id': 1,
                'name': 'sample_equipment_data.csv',
                'total_records': 15,
                'avg_flowrate': 175.5,
                'avg_pressure': 65.3,
                'avg_temperature': 195.2
            }
            
            # Simulate file selection
            upload_widget = main_window.upload_widget
            upload_widget.selected_file_path = sample_csv_path
            upload_widget.file_path_label.setText(sample_csv_path)
            upload_widget.upload_button.setEnabled(True)
            
            # Trigger upload
            upload_widget._upload_file()
            
            # Verify upload was called
            assert mock_upload.called, "Upload method should be called"
            results.add_pass("Upload functionality works")
    except Exception as e:
        results.add_fail("Upload functionality works", str(e))
    
    # Test upload completion handling
    try:
        dataset_info = {
            'id': 1,
            'name': 'sample_equipment_data.csv',
            'total_records': 15,
            'avg_flowrate': 175.5,
            'avg_pressure': 65.3,
            'avg_temperature': 195.2
        }
        
        main_window._handle_upload_completed(dataset_info)
        
        assert main_window.current_dataset is not None
        assert main_window.current_dataset['id'] == 1
        assert main_window.tab_widget.currentIndex() == 1  # Should switch to dashboard
        results.add_pass("Upload completion switches to dashboard")
    except Exception as e:
        results.add_fail("Upload completion switches to dashboard", str(e))
    
    return results



def test_dashboard_display():
    """Test 3: Dashboard displays correctly."""
    print("\n" + "=" * 60)
    print("Test 3: Dashboard Display Verification")
    print("=" * 60)
    
    results = WorkflowTestResults()
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Create main window with dataset
    try:
        config = get_config()
        api_client = APIClient(base_url=config.api_base_url)
        user_info = {'username': 'testuser', 'user_id': 1, 'token': 'test_token'}
        main_window = MainWindow(api_client, user_info)
        
        # Set current dataset
        main_window.current_dataset = {
            'id': 1,
            'name': 'test_data.csv',
            'total_records': 15,
            'avg_flowrate': 175.5,
            'avg_pressure': 65.3,
            'avg_temperature': 195.2,
            'type_distribution': {
                'Pump': 5,
                'Reactor': 4,
                'Heat Exchanger': 6
            }
        }
        results.add_pass("Main window with dataset created")
    except Exception as e:
        results.add_fail("Main window with dataset created", str(e))
        return results
    
    # Test dashboard widgets exist
    try:
        assert hasattr(main_window, 'summary_widget'), "Missing summary_widget"
        assert hasattr(main_window, 'data_table_widget'), "Missing data_table_widget"
        assert hasattr(main_window, 'chart_widget'), "Missing chart_widget"
        results.add_pass("Dashboard widgets exist")
    except AssertionError as e:
        results.add_fail("Dashboard widgets exist", str(e))

    # Test summary widget displays data
    try:
        with patch.object(api_client, 'get_dataset_summary') as mock_summary:
            mock_summary.return_value = main_window.current_dataset
            
            main_window.summary_widget.load_summary(1)
            
            # Verify summary widget has data
            assert main_window.summary_widget.total_label.text() != "0"
            results.add_pass("Summary widget displays data")
    except Exception as e:
        results.add_fail("Summary widget displays data", str(e))
    
    # Test data table widget
    try:
        with patch.object(api_client, 'get_dataset_data') as mock_data:
            mock_data.return_value = {
                'results': [
                    {
                        'equipment_name': 'Pump-A1',
                        'equipment_type': 'Pump',
                        'flowrate': 150.5,
                        'pressure': 45.2,
                        'temperature': 85.0
                    }
                ]
            }
            
            main_window.data_table_widget.load_data(1)
            
            # Verify table has data
            assert main_window.data_table_widget.table.rowCount() > 0
            results.add_pass("Data table widget displays data")
    except Exception as e:
        results.add_fail("Data table widget displays data", str(e))
    
    # Test chart widget
    try:
        type_distribution = main_window.current_dataset['type_distribution']
        main_window.chart_widget.plot_distribution(type_distribution)
        
        # Verify chart was created
        assert main_window.chart_widget.canvas is not None
        results.add_pass("Chart widget displays visualization")
    except Exception as e:
        results.add_fail("Chart widget displays visualization", str(e))
    
    return results



def test_history_navigation():
    """Test 4: History navigation."""
    print("\n" + "=" * 60)
    print("Test 4: History Navigation")
    print("=" * 60)
    
    results = WorkflowTestResults()
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Create main window
    try:
        config = get_config()
        api_client = APIClient(base_url=config.api_base_url)
        user_info = {'username': 'testuser', 'user_id': 1, 'token': 'test_token'}
        main_window = MainWindow(api_client, user_info)
        results.add_pass("Main window created")
    except Exception as e:
        results.add_fail("Main window created", str(e))
        return results
    
    # Test history widget exists
    try:
        assert hasattr(main_window, 'history_widget'), "Missing history_widget"
        assert main_window.history_widget is not None
        results.add_pass("History widget exists")
    except AssertionError as e:
        results.add_fail("History widget exists", str(e))
    
    # Test history widget is third tab
    try:
        history_tab = main_window.tab_widget.widget(2)
        assert history_tab is main_window.history_widget
        tab_text = main_window.tab_widget.tabText(2)
        assert tab_text == "History"
        results.add_pass("History widget is third tab")
    except AssertionError as e:
        results.add_fail("History widget is third tab", str(e))

    # Test loading history
    try:
        with patch.object(api_client, 'get_datasets') as mock_datasets:
            mock_datasets.return_value = [
                {
                    'id': 1,
                    'name': 'dataset1.csv',
                    'uploaded_at': '2025-11-22T10:00:00Z',
                    'total_records': 10
                },
                {
                    'id': 2,
                    'name': 'dataset2.csv',
                    'uploaded_at': '2025-11-22T11:00:00Z',
                    'total_records': 15
                }
            ]
            
            main_window.history_widget.load_datasets()
            
            # Verify datasets were loaded
            assert main_window.history_widget.dataset_list.count() == 2
            results.add_pass("History widget loads datasets")
    except Exception as e:
        results.add_fail("History widget loads datasets", str(e))
    
    # Test dataset selection signal
    try:
        signal_received = []
        main_window.history_widget.dataset_selected.connect(lambda x: signal_received.append(x))
        
        # Select first item
        main_window.history_widget.dataset_list.setCurrentRow(0)
        main_window.history_widget._handle_load_button_click()
        
        assert len(signal_received) == 1
        assert signal_received[0] == 1
        results.add_pass("History widget emits dataset selection signal")
    except Exception as e:
        results.add_fail("History widget emits dataset selection signal", str(e))
    
    # Test main window handles dataset selection
    try:
        with patch.object(api_client, 'get_dataset_summary') as mock_summary:
            with patch.object(api_client, 'get_dataset_data') as mock_data:
                mock_summary.return_value = {
                    'id': 1,
                    'name': 'dataset1.csv',
                    'total_records': 10,
                    'avg_flowrate': 150.0,
                    'avg_pressure': 45.0,
                    'avg_temperature': 85.0,
                    'type_distribution': {'Pump': 5}
                }
                mock_data.return_value = {'results': []}
                
                main_window.load_dataset(1)
                
                # Process events to allow async operations to complete
                app.processEvents()
                
                assert main_window.current_dataset is not None
                assert main_window.current_dataset['id'] == 1
                assert main_window.tab_widget.currentIndex() == 1  # Should switch to dashboard
                results.add_pass("Main window loads selected dataset")
    except Exception as e:
        results.add_fail("Main window loads selected dataset", str(e))
    
    return results



def test_pdf_download():
    """Test 5: PDF download."""
    print("\n" + "=" * 60)
    print("Test 5: PDF Download")
    print("=" * 60)
    
    results = WorkflowTestResults()
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Create main window with dataset
    try:
        config = get_config()
        api_client = APIClient(base_url=config.api_base_url)
        user_info = {'username': 'testuser', 'user_id': 1, 'token': 'test_token'}
        main_window = MainWindow(api_client, user_info)
        
        main_window.current_dataset = {
            'id': 1,
            'name': 'test_data.csv',
            'total_records': 15
        }
        results.add_pass("Main window with dataset created")
    except Exception as e:
        results.add_fail("Main window with dataset created", str(e))
        return results
    
    # Test report action exists
    try:
        assert hasattr(main_window, '_handle_report_action'), "Missing _handle_report_action"
        results.add_pass("Report action handler exists")
    except AssertionError as e:
        results.add_fail("Report action handler exists", str(e))
    
    # Test PDF download with no dataset
    try:
        main_window.current_dataset = None
        
        with patch.object(main_window, 'show_info') as mock_info:
            main_window._handle_report_action()
            
            mock_info.assert_called_once()
            results.add_pass("Shows info when no dataset loaded")
    except Exception as e:
        results.add_fail("Shows info when no dataset loaded", str(e))

    # Test successful PDF download
    try:
        main_window.current_dataset = {
            'id': 1,
            'name': 'test_data.csv',
            'total_records': 15
        }
        
        with patch('ui.main_window.QFileDialog.getSaveFileName') as mock_dialog:
            mock_dialog.return_value = ('/tmp/test_report.pdf', 'PDF Files (*.pdf)')
            
            with patch('ui.main_window.QProgressDialog') as MockProgress:
                mock_progress = MagicMock()
                MockProgress.return_value = mock_progress
                
                with patch.object(api_client, 'download_report') as mock_download:
                    mock_download.return_value = '/tmp/test_report.pdf'
                    
                    with patch.object(main_window, 'show_info') as mock_info:
                        main_window._handle_report_action()
                        
                        mock_download.assert_called_once_with(1, '/tmp/test_report.pdf')
                        mock_info.assert_called_once()
                        results.add_pass("PDF download completes successfully")
    except Exception as e:
        results.add_fail("PDF download completes successfully", str(e))
    
    # Test PDF download error handling
    try:
        with patch('ui.main_window.QFileDialog.getSaveFileName') as mock_dialog:
            mock_dialog.return_value = ('/tmp/test_report.pdf', 'PDF Files (*.pdf)')
            
            with patch('ui.main_window.QProgressDialog') as MockProgress:
                mock_progress = MagicMock()
                MockProgress.return_value = mock_progress
                
                with patch.object(api_client, 'download_report') as mock_download:
                    mock_download.side_effect = Exception("Network error")
                    
                    with patch.object(main_window, 'show_error') as mock_error:
                        main_window._handle_report_action()
                        
                        mock_error.assert_called_once()
                        results.add_pass("PDF download handles errors")
    except Exception as e:
        results.add_fail("PDF download handles errors", str(e))
    
    return results



def test_complete_workflow_integration():
    """Test 6: Complete workflow integration."""
    print("\n" + "=" * 60)
    print("Test 6: Complete Workflow Integration")
    print("=" * 60)
    
    results = WorkflowTestResults()
    app = QApplication.instance() or QApplication(sys.argv)
    
    try:
        config = get_config()
        api_client = APIClient(base_url=config.api_base_url)
        
        # Step 1: Login
        with patch.object(api_client, 'login') as mock_login:
            mock_login.return_value = {
                'token': 'test_token',
                'username': 'testuser',
                'user_id': 1
            }
            
            login_dialog = LoginDialog(api_client)
            login_dialog.username_input.setText("testuser")
            login_dialog.password_input.setText("testpass123")
            
            user_info = None
            def capture_user_info(info):
                nonlocal user_info
                user_info = info
            
            login_dialog.login_successful.connect(capture_user_info)
            login_dialog._handle_login()
            
            assert user_info is not None
            results.add_pass("Step 1: Login successful")
        
        # Step 2: Create main window
        main_window = MainWindow(api_client, user_info)
        assert main_window is not None
        results.add_pass("Step 2: Main window created")
        
        # Step 3: Upload CSV
        with patch.object(api_client, 'upload_dataset') as mock_upload:
            mock_upload.return_value = {
                'id': 1,
                'name': 'sample.csv',
                'total_records': 15,
                'avg_flowrate': 175.5,
                'avg_pressure': 65.3,
                'avg_temperature': 195.2
            }
            
            sample_csv = os.path.join(os.path.dirname(__file__), '..', 'backend', 'sample_equipment_data.csv')
            main_window.upload_widget.selected_file_path = sample_csv
            main_window.upload_widget._upload_file()
            
            assert mock_upload.called
            results.add_pass("Step 3: CSV upload triggered")

        # Step 4: Dashboard displays data
        dataset_info = mock_upload.return_value
        main_window._handle_upload_completed(dataset_info)
        
        assert main_window.current_dataset is not None
        assert main_window.tab_widget.currentIndex() == 1
        results.add_pass("Step 4: Dashboard displays after upload")
        
        # Step 5: Load history
        with patch.object(api_client, 'get_datasets') as mock_datasets:
            mock_datasets.return_value = [
                {'id': 1, 'name': 'sample.csv', 'uploaded_at': '2025-11-22T10:00:00Z', 'total_records': 15}
            ]
            
            main_window.history_widget.load_datasets()
            assert main_window.history_widget.dataset_list.count() == 1
            results.add_pass("Step 5: History loaded")
        
        # Step 6: Select from history
        with patch.object(api_client, 'get_dataset_summary') as mock_summary:
            with patch.object(api_client, 'get_dataset_data') as mock_data:
                mock_summary.return_value = dataset_info
                mock_data.return_value = {'results': []}
                
                main_window.load_dataset(1)
                app.processEvents()
                assert main_window.current_dataset['id'] == 1
                results.add_pass("Step 6: Dataset selected from history")
        
        # Step 7: Download PDF
        with patch('ui.main_window.QFileDialog.getSaveFileName') as mock_dialog:
            mock_dialog.return_value = ('/tmp/report.pdf', 'PDF Files (*.pdf)')
            
            with patch('ui.main_window.QProgressDialog') as MockProgress:
                mock_progress = MagicMock()
                MockProgress.return_value = mock_progress
                
                with patch.object(api_client, 'download_report') as mock_download:
                    mock_download.return_value = '/tmp/report.pdf'
                    
                    with patch.object(main_window, 'show_info'):
                        main_window._handle_report_action()
                        assert mock_download.called
                        results.add_pass("Step 7: PDF downloaded")
        
    except Exception as e:
        results.add_fail("Complete workflow integration", str(e))
        import traceback
        traceback.print_exc()
    
    return results



def main():
    """Run all workflow tests."""
    print("=" * 60)
    print("PyQt5 Desktop App - Complete Workflow Test (Task 27.2)")
    print("=" * 60)
    print("\nThis test verifies the complete workflow:")
    print("  1. Login flow")
    print("  2. CSV upload with sample data")
    print("  3. Dashboard display verification")
    print("  4. History navigation")
    print("  5. PDF download")
    print("  6. Complete workflow integration")
    print()
    
    all_results = []
    
    # Run all test suites
    all_results.append(test_login_flow())
    all_results.append(test_csv_upload())
    all_results.append(test_dashboard_display())
    all_results.append(test_history_navigation())
    all_results.append(test_pdf_download())
    all_results.append(test_complete_workflow_integration())
    
    # Calculate totals
    total_passed = sum(r.passed for r in all_results)
    total_failed = sum(r.failed for r in all_results)
    total_tests = total_passed + total_failed
    
    # Print summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print()
    
    if total_failed == 0:
        print("✓ ALL TESTS PASSED")
        print("\nTask 27.2 is COMPLETE!")
        print("\nAll workflow components verified:")
        print("  ✓ Login flow works correctly")
        print("  ✓ CSV upload with sample data successful")
        print("  ✓ Dashboard displays data correctly")
        print("  ✓ History navigation functional")
        print("  ✓ PDF download works")
        print("  ✓ Complete workflow integration verified")
        print("\nThe PyQt5 desktop application is ready for use!")
    else:
        print("✗ SOME TESTS FAILED")
        print("\nPlease review the failed tests above.")
    
    print("=" * 60)
    
    return total_failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
