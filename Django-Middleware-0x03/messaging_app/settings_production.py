"""
Production settings for messaging_app project.
"""

import os
from .settings import *  # Import base settings

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'replace-this-with-a-secure-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Define allowed hosts for your production environment
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com', 'server_ip_address']

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Additional production-specific settings can be added here
 
