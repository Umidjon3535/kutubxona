"""
Django settings for kutubxona project.
Production (Vercel) + Development (local) uchun sozlamalar.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-kutubxona-secret-key-change-in-production-2024'
)

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.vercel.app',
    '.now.sh',
    '*',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'library',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'kutubxona.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'kutubxona.wsgi.application'

# ------------------------------------------------------------------ #
#  Database — PostgreSQL (Vercel) yoki SQLite (local)                 #
# ------------------------------------------------------------------ #
DATABASE_URL = os.environ.get('DATABASE_URL', '')

if DATABASE_URL:
    # Vercel Postgres yoki boshqa PostgreSQL
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    # Local development — SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ------------------------------------------------------------------ #
#  Password validation                                                 #
# ------------------------------------------------------------------ #
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ------------------------------------------------------------------ #
#  Internationalization                                                #
# ------------------------------------------------------------------ #
LANGUAGE_CODE = 'uz-uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------ #
#  Static files — WhiteNoise                                          #
# ------------------------------------------------------------------ #
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ------------------------------------------------------------------ #
#  Media files                                                         #
# ------------------------------------------------------------------ #
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'library.User'

# Auth URLs
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/auth/login/'

# Messages
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'error',
}

# Error handlers
HANDLER404 = 'library.views.home_views.custom_404'
HANDLER500 = 'library.views.home_views.custom_500'
HANDLER403 = 'library.views.home_views.custom_403'
