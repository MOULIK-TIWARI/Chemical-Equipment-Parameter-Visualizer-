"""
Custom middleware for authentication and token validation.
"""
from django.utils.deprecation import MiddlewareMixin
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser


class TokenValidationMiddleware(MiddlewareMixin):
    """
    Middleware to validate authentication tokens on each request.
    This provides additional token validation beyond DRF's built-in authentication.
    """
    
    def process_request(self, request):
        """
        Validate the authentication token if present in the request.
        """
        # Get the authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith('Token '):
            token_key = auth_header.split(' ')[1]
            
            try:
                # Validate that the token exists and is active
                token = Token.objects.select_related('user').get(key=token_key)
                
                # Check if the user is active
                if not token.user.is_active:
                    request.user = AnonymousUser()
                    return None
                
                # Token is valid, user will be set by DRF authentication
                
            except Token.DoesNotExist:
                # Invalid token, user will remain anonymous
                request.user = AnonymousUser()
        
        return None
