"""
Configuración del proyecto Ferias Locales.
Los valores sensibles se leen desde el archivo .env (ver .env.example).
"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Carga las variables del archivo .env (no se sube a GitHub)
load_dotenv(BASE_DIR / '.env')

# La clave ya no está escrita en el código
SECRET_KEY = os.getenv('SECRET_KEY')

# El .env guarda texto: se compara con 'True'. Por defecto queda desactivado
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Texto separado por comas convertido en lista
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'eventos',
    'feria',
    'usuarios',
    'carrito',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Si un visitante sin sesión entra a una vista protegida, va a esta ruta
LOGIN_URL = 'login'

# Credenciales de Webpay: viven solo en el .env
WEBPAY_COMMERCE_CODE = os.getenv('WEBPAY_COMMERCE_CODE')
WEBPAY_API_KEY = os.getenv('WEBPAY_API_KEY')
WEBPAY_ENV = os.getenv('WEBPAY_ENV', 'TEST')

# Con HTTPS real (despliegue) se activan cookies seguras y HSTS
if os.getenv('USE_HTTPS') == 'True':
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# La aplicación no envía correos, así que no se configura un backend de producción
SILENCED_SYSTEM_CHECKS = ['mail.E001']
