"""
Django settings for eiger project.

Generated by 'django-admin startproject' using Django 4.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
from pathlib import Path
from typing import Tuple

import django_stubs_ext
import structlog
from decouple import AutoConfig

# Monkeypatching Django, so stubs will work for all generics,
# see: https://github.com/typeddjango/django-stubs
django_stubs_ext.monkeypatch()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Loading `.env` files
# See docs: https://gitlab.com/mkleehammer/autoconfig
config = AutoConfig(search_path=BASE_DIR)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Application definition

INSTALLED_APPS: Tuple[str, ...] = (
    # Default django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # django-admin:
    'django.contrib.admindocs',
    'django.contrib.admin',
)

MIDDLEWARE: Tuple[str, ...] = (
    # Logging:
    'eiger.logging.LoggingContextVarsMiddleware',
    # Django
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'eiger.urls'

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

WSGI_APPLICATION = 'eiger.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    # We use these formatters in our `'handlers'` configuration.
    # Probably, you won't need to modify these lines.
    # Unless, you know what you are doing.
    'formatters': {
        'json_formatter': {
            '()': structlog.stdlib.ProcessorFormatter,
            'processor': structlog.processors.JSONRenderer(),
        },
        'console': {
            '()': structlog.stdlib.ProcessorFormatter,
            'processor': structlog.processors.KeyValueRenderer(
                key_order=['timestamp', 'level', 'event', 'logger'],
            ),
        },
    },
    # You can easily swap `key/value` (default) output and `json` ones.
    # Use `'json_console'` if you need `json` logs.
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
        'json_console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json_formatter',
        },
    },
    # These loggers are required by our app:
    # - django is required when using `logger.getLogger('django')`
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        },
        'security': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
_PASS = 'django.contrib.auth.password_validation'
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': '{0}.UserAttributeSimilarityValidator'.format(_PASS)},
    {'NAME': '{0}.MinimumLengthValidator'.format(_PASS)},
    {'NAME': '{0}.CommonPasswordValidator'.format(_PASS)},
    {'NAME': '{0}.NumericPasswordValidator'.format(_PASS)},
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

if DEBUG:
    STATIC_ROOT = '.static'
    ALLOWED_HOSTS = [
        config('DOMAIN_NAME'),
        'localhost',
        '0.0.0.0',  # noqa: S104
        '127.0.0.1',
        '[::1]',
        'web',
    ]
else:
    STATIC_ROOT = '/var/www/django/static/'
    ALLOWED_HOSTS = [
        config('DOMAIN_NAME'),
        # We need this value for `healthcheck` to work:
        'localhost',
        '0.0.0.0',
    ]
