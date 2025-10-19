# backend_django/apex_project/settings.py

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-j!w%g1q6m!^a@t!w^c6g^w0!3^g2^g1s!g!g1s^g1s^g1s^g1s^g1s^g1s^g1s^g1s^g1s^g1s^g1s^g1s^g1s^g1s^g1s^g1s^g1s^g1s^g1s^g1s'


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*'] # Use '*' for development/Replit/Render. Be more restrictive in final production.


# --- INSTALLED APPS (REPLACE ESTA SECCIÓN) ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Custom Apps
    'rest_framework', # Required for API endpoints
    'api',          # Your new API application
    'corsheaders',  # Required for React frontend connection
]


# --- MIDDLEWARE (REPLACE ESTA SECCIÓN) ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # CORS Middleware must be before CommonMiddleware (IMPORTANT)
    'corsheaders.middleware.CorsMiddleware', 
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'apex_project.urls'

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

WSGI_APPLICATION = 'apex_project.wsgi.application'


# --- MongoDB Atlas Connection (NEW SECTION) ---
# NOTE: This line reads the URI from the environment (Render) or uses the default for local testing.
MONGO_URI = os.environ.get(
    'MONGO_URI', 
    'mongodb+srv://dynamic:Peru2022@Cluster0.6etb2.mongodb.net/?retryWrites=true&w=majority'
)

DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'footwear', # Your database name in Atlas
        'ENFORCE_SCHEMA': False, # Important for NoSQL flexibility
        'CONN_MAX_AGE': 0,
        'CLIENT': {
            'host': MONGO_URI,
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # ... (deja el código de validación de contraseña)
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- CORS Settings (NEW SECTION - Required for React) ---
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000", # Common for React Dev Server
    # Add your Vercel/Netlify URL here after deployment (e.g., "https://mvp-planificacion.vercel.app")
]

# Allow all common methods for the API endpoints (GET, POST)
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]
