# backend_django/apex_project/settings.py

import os
from pathlib import Path
import dj_database_url # <--- NUEVA IMPORTACIÓN: Para leer la URL de PostgreSQL de Render

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
# Se recomienda leer la SECRET_KEY desde una variable de entorno en producción
SECRET_KEY = os.environ.get(
    'SECRET_KEY', 
    'django-insecure-j!w%g1q6m!^a@t!w^c6g^w0!3^g2^g1s!g!g1s^g1s^g1s^g1s^g1s^g1s^g1s^g1s^g1s^g1s^g1s^g1s^g1s^g1s^g1s^g1s^g1s^g1s^g1s^g1s'
)


# SECURITY WARNING: don't run with debug turned on in production!
# Usamos una variable de entorno para controlar el DEBUG en Render
DEBUG = os.environ.get('DEBUG') == 'True' 

# ALLOWED_HOSTS
# Render te proporciona un host, pero podemos mantener '*' o usar el nombre de dominio de Render
ALLOWED_HOSTS = ['*'] 


# ----------------------------------------------------------------------
# INSTALLED APPS (ACTUALIZADO PARA POSTGRESQL/DJANGO 4.2)
# ----------------------------------------------------------------------
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


# ----------------------------------------------------------------------
# MIDDLEWARE (SIN CAMBIOS, PERO FUNCIONA CON DJANGO 4.2)
# ----------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Middleware para Gunicorn y Render (esenciales para HTTP seguro)
    'whitenoise.middleware.WhiteNoiseMiddleware', # <--- RECOMENDADO: Añadir si sirves static files
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


# ----------------------------------------------------------------------
# BASE DE DATOS (CONFIGURACIÓN PARA POSTGRESQL EN RENDER) <--- ¡CAMBIO CRUCIAL!
# ----------------------------------------------------------------------
# Elimina MONGO_URI y la configuración Djongo/MongoDB.

# Usa dj_database_url para leer automáticamente la variable de entorno DATABASE_URL
# proporcionada por Render y configurar el backend de PostgreSQL.


# TEMPORAL: para que el comando makemigrations funcione localmente sin PostgreSQL
DATABASES = {
    'default': dj_database_url.config(
        # Render inyectará su DATABASE_URL aquí
        default=os.environ.get('DATABASE_URL'), 
        conn_max_age=600, 
        # conn_health_check=True, 
    )
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


# ----------------------------------------------------------------------
# ARCHIVOS ESTÁTICOS Y CONFIGURACIÓN DE PRODUCCIÓN (¡IMPORTANTE PARA RENDER!)
# ----------------------------------------------------------------------
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles' # Directorio donde 'collectstatic' reunirá los archivos

# Opcional: Configuración para WhiteNoise (si se usa para servir estáticos en producción)
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' 


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
# Se usa BigAutoField para evitar errores comunes de compatibilidad con PostgreSQL y migraciones.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- CORS Settings (SIN CAMBIOS) ---
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

# --- Configuración para suprimir warnings en loaddata (Acelera el log) ---
import warnings
# Desactiva los warnings de "naive datetime" que ralentizan el log
warnings.filterwarnings(
    'ignore',
    message='DateTimeField .* received a naive datetime',
    module='django.db.models.fields'
)