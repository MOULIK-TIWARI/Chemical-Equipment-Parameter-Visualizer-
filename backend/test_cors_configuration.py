"""
Test script to verify CORS configuration is working correctly.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chemical_equipment_analytics.settings')
django.setup()

from django.conf import settings
from django.test import RequestFactory
from corsheaders.middleware import CorsMiddleware


def test_cors_configuration():
    """Test that CORS is properly configured."""
    print("Testing CORS Configuration...")
    print("-" * 50)
    
    # Check if corsheaders is in INSTALLED_APPS
    assert 'corsheaders' in settings.INSTALLED_APPS, "corsheaders not in INSTALLED_APPS"
    print("✓ corsheaders is in INSTALLED_APPS")
    
    # Check if CorsMiddleware is in MIDDLEWARE
    middleware_classes = [m for m in settings.MIDDLEWARE]
    assert 'corsheaders.middleware.CorsMiddleware' in middleware_classes, "CorsMiddleware not in MIDDLEWARE"
    print("✓ CorsMiddleware is in MIDDLEWARE")
    
    # Check CorsMiddleware position (should be before CommonMiddleware)
    cors_index = middleware_classes.index('corsheaders.middleware.CorsMiddleware')
    common_index = middleware_classes.index('django.middleware.common.CommonMiddleware')
    assert cors_index < common_index, "CorsMiddleware should be before CommonMiddleware"
    print("✓ CorsMiddleware is correctly positioned before CommonMiddleware")
    
    # Check CORS_ALLOWED_ORIGINS
    assert hasattr(settings, 'CORS_ALLOWED_ORIGINS'), "CORS_ALLOWED_ORIGINS not configured"
    assert 'http://localhost:3000' in settings.CORS_ALLOWED_ORIGINS, "localhost:3000 not in allowed origins"
    assert 'http://127.0.0.1:3000' in settings.CORS_ALLOWED_ORIGINS, "127.0.0.1:3000 not in allowed origins"
    print("✓ CORS_ALLOWED_ORIGINS includes React dev server URLs")
    print(f"  Allowed origins: {settings.CORS_ALLOWED_ORIGINS}")
    
    # Check CORS_ALLOW_CREDENTIALS
    assert hasattr(settings, 'CORS_ALLOW_CREDENTIALS'), "CORS_ALLOW_CREDENTIALS not configured"
    assert settings.CORS_ALLOW_CREDENTIALS is True, "CORS_ALLOW_CREDENTIALS should be True"
    print("✓ CORS_ALLOW_CREDENTIALS is set to True")
    
    # Test middleware instantiation
    try:
        middleware = CorsMiddleware(lambda req: None)
        print("✓ CorsMiddleware instantiates without errors")
    except Exception as e:
        raise AssertionError(f"Failed to instantiate CorsMiddleware: {e}")
    
    print("-" * 50)
    print("✅ All CORS configuration tests passed!")
    print("\nConfiguration Summary:")
    print(f"  - Package: django-cors-headers")
    print(f"  - Allowed Origins: {settings.CORS_ALLOWED_ORIGINS}")
    print(f"  - Allow Credentials: {settings.CORS_ALLOW_CREDENTIALS}")
    print("\nThe backend is ready to accept requests from the React dev server.")


if __name__ == '__main__':
    try:
        test_cors_configuration()
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        exit(1)
