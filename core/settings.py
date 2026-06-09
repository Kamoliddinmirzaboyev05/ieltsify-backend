import os
from pathlib import Path
from dotenv import load_dotenv
from decouple import config


# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

SECURE_SSL_REDIRECT = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False


ALLOWED_HOSTS = ['*']

# Security settings for production
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # packages
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_yasg',
    'django_extensions',
    'django_filters',

    # apps
    'accounts',
    'modules',
    'attempts',
    'subscriptions',
    'mockexams',
    'ai_services',
]

# Payment Gateway Settings
CLICK_SERVICE_ID = config('CLICK_SERVICE_ID', default='12345', cast=int)
CLICK_MERCHANT_ID = config('CLICK_MERCHANT_ID', default='67890', cast=int)
CLICK_SECRET_KEY = config('CLICK_SECRET_KEY', default='')
CLICK_CALLBACK_URL = config('CLICK_CALLBACK_URL', default='https://yourdomain.com/api/subscriptions/payments/callback/')

PAYME_SERVICE_ID = config('PAYME_SERVICE_ID', default='54321', cast=int)
PAYME_MERCHANT_ID = config('PAYME_MERCHANT_ID', default='98765', cast=int)
PAYME_SECRET_KEY = config('PAYME_SECRET_KEY', default='')
PAYME_CALLBACK_URL = config('PAYME_CALLBACK_URL', default='https://yourdomain.com/api/subscriptions/payments/callback/')

# Payment Gateway URLs
CLICK_PAYMENT_URL = "https://click.uz/pay"
PAYME_PAYMENT_URL = "https://checkout.payme.uz"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True

SWAGGER_SETTINGS = {
   'SECURITY_DEFINITIONS': {
      'Basic': {
            'type': 'basic'
      },
      'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
      }
   }
}

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    # 'DEFAULT_PERMISSION_CLASSES': [
    #     'rest_framework.permissions.IsAuthenticated',
    # ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# JWT Settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv('JWT_ACCESS_TOKEN_LIFETIME', '60'))),
    'REFRESH_TOKEN_LIFETIME': timedelta(hours=int(os.getenv('JWT_REFRESH_TOKEN_LIFETIME', '24'))),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': os.getenv('JWT_SECRET_KEY', SECRET_KEY),
}

ROOT_URLCONF = 'core.urls'

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

WSGI_APPLICATION = 'core.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Application level constants
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_VERIFICATION_CODE_TTL_MINUTES = 10
REFERRAL_INVITER_REWARD = 100
REFERRAL_NEW_USER_REWARD = 25


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
]


# Internationalization
LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'




# # CORS settings
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
# ]
#
# # Email settings
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
# EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
# DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'IELTSify <noreply@ieltsify.com>')
# EMAIL_USE_TLS = True
#
# # Frontend URL
# FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
#
# # Google OAuth settings
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
# GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# Custom authentication backend to allow email login
AUTHENTICATION_BACKENDS = [
    'accounts.authentication.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'accounts': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
