import os
from pathlib import Path

import dj_database_url


# ============================================================
# BASE CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# ENVIRONMENT
# ============================================================

DEBUG = os.getenv("DEBUG", "True").lower() == "true"

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "dev-only-change-this-secret-key",
)

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        "ALLOWED_HOSTS",
        "127.0.0.1,localhost",
    ).split(",")
    if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CSRF_TRUSTED_ORIGINS",
        "",
    ).split(",")
    if origin.strip()
]


# ============================================================
# INSTALLED APPLICATIONS
# ============================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "core",
    "authentication",
    "records",
    "appointments",
    "billing",
]


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    "whitenoise.middleware.WhiteNoiseMiddleware",

    "core.middleware.AbuseRateLimitMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "core.middleware.SecurityHeadersMiddleware",
]


# ============================================================
# URL / APPLICATION CONFIGURATION
# ============================================================

ROOT_URLCONF = "urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [
            BASE_DIR / "templates",
        ],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.security_context",
            ],
        },
    },
]

WSGI_APPLICATION = "wsgi.application"


# ============================================================
# DATABASE
# ============================================================

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=not DEBUG,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# ============================================================
# CACHE
# ============================================================
# Used by the abuse/rate-limiting middleware.
#
# This is suitable for local development.
# For a multi-worker production deployment, we can later
# move this to a shared cache such as Redis if available.
# ============================================================

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "hospital-management-system-cache",
    }
}


# ============================================================
# PASSWORD SECURITY
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
        "OPTIONS": {
            "min_length": 10,
        },
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ============================================================
# INTERNATIONALIZATION
# ============================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


# ============================================================
# STATIC FILES
# ============================================================

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

if DEBUG:
    # Local development and automated tests
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": (
                "django.contrib.staticfiles.storage.StaticFilesStorage"
            ),
        },
    }
else:
    # Production
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": (
                "whitenoise.storage."
                "CompressedManifestStaticFilesStorage"
            ),
        },
    }


# ============================================================
# DEFAULT MODEL FIELD
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ============================================================
# AUTHENTICATION
# ============================================================

LOGIN_URL = "login"

LOGIN_REDIRECT_URL = "dashboard"

LOGOUT_REDIRECT_URL = "login"


# ============================================================
# SESSION SECURITY
# ============================================================

SESSION_COOKIE_HTTPONLY = True

SESSION_COOKIE_SAMESITE = "Lax"

CSRF_COOKIE_SAMESITE = "Lax"


# ============================================================
# GENERAL SECURITY HEADERS
# ============================================================

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

X_FRAME_OPTIONS = "DENY"


# ============================================================
# DEVELOPMENT / PRODUCTION SECURITY
# ============================================================

if not DEBUG:

    # HTTPS
    SECURE_SSL_REDIRECT = True

    # HSTS
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Secure cookies
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

else:

    # Local development runs over HTTP.
    SECURE_SSL_REDIRECT = False

    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

    SECURE_HSTS_SECONDS = 0


# ============================================================
# PRODUCTION SAFETY VALIDATION
# ============================================================

if not DEBUG and SECRET_KEY == "dev-only-change-this-secret-key":
    raise RuntimeError(
        "DJANGO_SECRET_KEY must be set when DEBUG=False."
    )


if not DEBUG and not ALLOWED_HOSTS:
    raise RuntimeError(
        "ALLOWED_HOSTS must be configured when DEBUG=False."
    )


# ============================================================
# LOGGING
# ============================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },

    "loggers": {
        "django.security": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}