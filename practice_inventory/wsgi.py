"""
WSGI config for practice_inventory project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import logging
import os

logger = logging.getLogger(__name__)

from django.core.wsgi import get_wsgi_application

logger.critical(f"wsgi.main: '.' = {os.path.abspath(".")}")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'practice_inventory.settings')

application = get_wsgi_application()
