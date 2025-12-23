
from django.conf import settings

def get_absolute_url(url):
    """Convert relative media URL to absolute URL"""
    if not url:
        return None
    
    # If it's already an absolute URL, return as is
    if url.startswith(('http://', 'https://')):
        return url
    
    # Build absolute URL
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
    return f"{site_url}{url}"