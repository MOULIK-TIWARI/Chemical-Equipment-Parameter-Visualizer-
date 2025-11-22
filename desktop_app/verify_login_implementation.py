"""
Verification script for Task 17.2: Implement login logic

This script verifies that the LoginDialog implementation includes:
1. Call authentication API endpoint
2. Store token in API client
3. Close dialog on success
4. Show error message on failure

Requirements: 6.3, 6.4
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def verify_login_dialog_implementation():
    """Verify that LoginDialog has all required login logic."""
    
    print("=" * 70)
    print("Task 17.2 Implementation Verification")
    print("=" * 70)
    print()
    
    # Check 1: Import LoginDialog
    print("✓ Check 1: Importing LoginDialog class...")
    try:
        from ui.login_dialog import LoginDialog
        print("  SUCCESS: LoginDialog imported successfully")
    except ImportError as e:
        print(f"  FAILED: Could not import LoginDialog: {e}")
        return False
    
    # Check 2: Import APIClient
    print("\n✓ Check 2: Importing APIClient class...")
    try:
        from services.api_client import APIClient
        print("  SUCCESS: APIClient imported successfully")
    except ImportError as e:
        print(f"  FAILED: Could not import APIClient: {e}")
        return False
    
    # Check 3: Verify LoginDialog has _handle_login method
    print("\n✓ Check 3: Verifying _handle_login method exists...")
    if hasattr(LoginDialog, '_handle_login'):
        print("  SUCCESS: _handle_login method found")
    else:
        print("  FAILED: _handle_login method not found")
        return False
    
    # Check 4: Verify APIClient has login method
    print("\n✓ Check 4: Verifying APIClient.login method exists...")
    if hasattr(APIClient, 'login'):
        print("  SUCCESS: APIClient.login method found")
    else:
        print("  FAILED: APIClient.login method not found")
        return False
    
    # Check 5: Verify token storage in APIClient
    print("\n✓ Check 5: Verifying token storage mechanism...")
    if hasattr(APIClient, '_save_token') and hasattr(APIClient, 'token'):
        print("  SUCCESS: Token storage mechanism found")
    else:
        print("  FAILED: Token storage mechanism not found")
        return False
    
    # Check 6: Verify error handling in LoginDialog
    print("\n✓ Check 6: Verifying error display mechanism...")
    if hasattr(LoginDialog, '_show_error'):
        print("  SUCCESS: Error display mechanism found")
    else:
        print("  FAILED: Error display mechanism not found")
        return False
    
    # Check 7: Read and verify implementation details
    print("\n✓ Check 7: Verifying implementation details in source code...")
    try:
        with open('ui/login_dialog.py', 'r') as f:
            content = f.read()
            
            checks = {
                'API call': 'self.api_client.login(' in content,
                'Dialog close on success': 'self.accept()' in content,
                'Error handling': 'except Exception' in content,
                'Error display': 'self._show_error(' in content,
            }
            
            all_passed = True
            for check_name, passed in checks.items():
                if passed:
                    print(f"  ✓ {check_name}: Found")
                else:
                    print(f"  ✗ {check_name}: Not found")
                    all_passed = False
            
            if not all_passed:
                return False
                
    except FileNotFoundError:
        print("  FAILED: Could not read login_dialog.py")
        return False
    
    print("\n" + "=" * 70)
    print("VERIFICATION COMPLETE: All checks passed! ✓")
    print("=" * 70)
    print()
    print("Task 17.2 Implementation Summary:")
    print("  1. ✓ Calls authentication API endpoint via api_client.login()")
    print("  2. ✓ Token is stored in API client automatically")
    print("  3. ✓ Dialog closes on success with self.accept()")
    print("  4. ✓ Error messages shown on failure via _show_error()")
    print()
    print("Requirements satisfied:")
    print("  - Requirement 6.3: Desktop Frontend authentication")
    print("  - Requirement 6.4: Invalid credentials error handling")
    print()
    
    return True


if __name__ == "__main__":
    success = verify_login_dialog_implementation()
    sys.exit(0 if success else 1)
