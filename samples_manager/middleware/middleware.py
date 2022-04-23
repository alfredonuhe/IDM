"""File used to store application middleware."""

from django.utils import timezone
from ..utilities import get_cern_timezone

class TimezoneMiddleware:
    """App timezone middleware."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """Returns user timezone. For now only local server timezone."""
        tz = get_cern_timezone()
        timezone.activate(tz)
        return self.get_response(request)

