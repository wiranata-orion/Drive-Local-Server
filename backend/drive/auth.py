"""
Custom authentication for shared password access.
"""
from rest_framework import authentication, exceptions
from django.conf import settings


class SharedPasswordAuthentication(authentication.BaseAuthentication):
    """
    Authenticate using a shared password.

    Accepts password via:
    - Authorization: Bearer <password>
    - X-Password header
    """

    def authenticate(self, request):
        # Get password from Authorization header or X-Password header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        password = None

        if auth_header.startswith('Bearer '):
            password = auth_header[7:]  # Remove 'Bearer '
        elif request.META.get('HTTP_X_PASSWORD'):
            password = request.META.get('HTTP_X_PASSWORD')

        if not password:
            return None

        # Check against configured shared password
        shared_password = getattr(settings, 'SHARED_PASSWORD', None)
        if not shared_password:
            raise exceptions.AuthenticationFailed('Server not configured with SHARED_PASSWORD')

        if password != shared_password:
            raise exceptions.AuthenticationFailed('Invalid password')

        # Return a dummy user-like object
        return (SharedPasswordUser(), None)

    def authenticate_header(self, request):
        return 'Bearer'


class SharedPasswordUser:
    """Dummy user object for authenticated requests."""

    def __init__(self):
        self.is_authenticated = True
        self.is_anonymous = False
        self.is_staff = False
        self.is_superuser = False

    @property
    def pk(self):
        return None

    def __str__(self):
        return 'shared-user'