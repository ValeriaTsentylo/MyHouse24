from pathlib import Path

from decouple import config
from dotenv import load_dotenv

# Load the environment to determine which .env file to use
ENVIRONMENT = config("ENVIRONMENT", default="local")

# Define the base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables based on the environment
if ENVIRONMENT == "local":
    load_dotenv(BASE_DIR / ".env_local")
else:
    load_dotenv(BASE_DIR / ".env_prod")

# Django secret key for encryption and security
SECRET_KEY = config("SECRET_KEY", default="insecure-dev-key-change-me")

# Enable/disable debug mode
DEBUG = config("DEBUG", default=False, cast=bool)

# Allowed hosts for server requests
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost",
    cast=lambda v: [s.strip() for s in v.split(",")],
)

# Installed apps, including Django's built-in apps and custom apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "allauth",
    "allauth.account",
    "django.contrib.sites",
    # custom apps
    "src.core",
    "src.users",
    "src.houses",
    "src.roles",
    "src.service",
    "src.payments_section",
    "src.statistic",
    "src.apartments",
]

# Middleware for handling requests and sessions
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

INTERNAL_IPS = [
    "127.0.0.1",
]

# debug_toolbar is a development-only dependency
if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

# URL configuration
ROOT_URLCONF = "config.urls"

AUTH_USER_MODEL = "users.User"

# Template configuration
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# WSGI application for handling requests in production
WSGI_APPLICATION = "config.wsgi.application"

# Database configuration
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="myhouse24"),
        "USER": config("DB_USER", default="myhouse24"),
        "PASSWORD": config("DB_PASSWORD", default="myhouse24"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

# Password validators for enhanced security
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Language and timezone settings
LANGUAGE_CODE = "uk"
TIME_ZONE = "Europe/Kyiv"
USE_I18N = True
USE_TZ = True

# Static and media files configuration
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Authentication backends, including custom and Allauth backends
AUTHENTICATION_BACKENDS = [
    "allauth.account.auth_backends.AuthenticationBackend",  # Allauth backend
]

# Celery configuration for background task processing
CELERY_BROKER_URL = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Email configuration for sending confirmation and notifications
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = config("EMAIL_HOST", default="localhost")
EMAIL_PORT = config("EMAIL_PORT", cast=int, default=25)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=False)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", cast=bool, default=False)

# Django Allauth email verification and signup settings
# Django Allauth configuration for user authentication via email
SITE_ID = 1
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3  # Expiry period for confirmation a link
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True  # Automatic login after email confirmation

# reCAPTCHA keys for form verification
RECAPTCHA_PUBLIC_KEY = config("RECAPTCHA_PUBLIC_KEY", default="")
RECAPTCHA_PRIVATE_KEY = config("RECAPTCHA_PRIVATE_KEY", default="")

# --- Security / logging hardening ---
# Everything below is inert during local development and turns on in production.

if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="",
    cast=lambda v: [s.strip() for s in v.split(",") if s.strip()],
)

if not DEBUG:
    SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "{levelname} {asctime} {name} {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "src": {"handlers": ["console"], "level": "DEBUG" if DEBUG else "INFO", "propagate": False},
    },
}
