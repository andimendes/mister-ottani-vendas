from pathlib import Path
from datetime import timedelta

# =====================================================================================
# Base do projeto
# =====================================================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# =====================================================================================
# Segurança
# =====================================================================================
SECRET_KEY = '1309513b7d88f67d8e7aca3eb6571aa509a1c18a33c2a70af4f5812440a4429f7ed4edca3cdca3889fc528371c4a17cf30f'
DEBUG = True
ALLOWED_HOSTS = []

# =====================================================================================
# Apps instalados
# =====================================================================================
INSTALLED_APPS = [
    # Seus apps
    'gestao.apps.GestaoConfig',
    'vendas.apps.VendasConfig',

    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Terceiros
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
]

# =====================================================================================
# Middlewares
# =====================================================================================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',            # deve vir antes do CommonMiddleware
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# =====================================================================================
# URL Configuration
# =====================================================================================
ROOT_URLCONF = 'misterottani_crm.urls'

# =====================================================================================
# Templates
# =====================================================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],        # se tiver templates em pastas custom, adicione aqui
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

# =====================================================================================
# WSGI
# =====================================================================================
WSGI_APPLICATION = 'misterottani_crm.wsgi.application'

# =====================================================================================
# Banco de Dados
# =====================================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# =====================================================================================
# Autenticação e Senhas
# =====================================================================================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# =====================================================================================
# Internacionalização
# =====================================================================================
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# =====================================================================================
# Arquivos estáticos
# =====================================================================================
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =====================================================================================
# CORS
# =====================================================================================
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # seu frontend local
]

# =====================================================================================
# Django REST Framework + Simple JWT
# =====================================================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}
