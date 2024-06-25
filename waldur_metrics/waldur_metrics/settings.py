import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", 'insecure-secret')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'waldur_metrics',
]

MIDDLEWARE = []

ROOT_URLCONF = 'waldur_metrics.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'waldur_metrics.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get("METRICS_DB_NAME", 'waldur_metrics'),
        'USER': os.environ.get("METRICS_DB_USER", 'postgres'),
        'PASSWORD': os.environ.get("METRICS_DB_PASSWORD", '1234'),
        'HOST': os.environ.get("METRICS_DB_HOST", '127.0.0.1'),
        'PORT': os.environ.get("METRICS_DB_PORT", '5433'),
    },
    'waldur': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get("SOURCE_DB_NAME", 'waldur'),
        'USER': os.environ.get("SOURCE_DB_USER", 'postgres'),
        'PASSWORD': os.environ.get("SOURCE_DB_PASSWORD", '1234'),
        'HOST': os.environ.get("SOURCE_DB_HOST", '127.0.0.1'),
        'PORT': os.environ.get("SOURCE_DB_PORT", '5433'),
    },
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = False

USE_L10N = False

USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
