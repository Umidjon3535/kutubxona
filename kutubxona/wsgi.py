"""
WSGI config for kutubxona project.
Vercel uchun 'app' va 'application' ikkalasi ham eksport qilinadi.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kutubxona.settings')

application = get_wsgi_application()

# Vercel @vercel/python 'app' nomini qidiradi
app = application
