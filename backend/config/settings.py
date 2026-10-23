"""Réglages Django de SteamLens.

Référence : https://docs.djangoproject.com/en/6.1/ref/settings/
"""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# Les secrets viennent de l'environnement ou de backend/.env (ignoré par git) ;
# backend/.env.example liste toutes les variables.
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

DEVELOPMENT_SECRET_KEY = "django-insecure-cle-de-developpement-seulement"
SECRET_KEY = env.str("DJANGO_SECRET_KEY", default=DEVELOPMENT_SECRET_KEY)

DEBUG = env.bool("DJANGO_DEBUG", default=True)

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "0.0.0.0"])

# Clés des API externes : vide = la source est sautée à l'import.
API_KEYS = {
    name: env.str(name, default="")
    for name in (
        "STEAM_API_KEY",
        "TWITCH_CLIENT_ID",
        "TWITCH_CLIENT_SECRET",
        "RAWG_API_KEY",
        "ITAD_API_KEY",
        "KAGGLE_USERNAME",
        "KAGGLE_KEY",
    )
}


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "rest_framework",
    "catalog",
    "geography",
    "ingestion",
    "players",
    "pricing",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


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


LANGUAGE_CODE = "fr-fr"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"


MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.console.EmailBackend",
    },
}


# API REST : pagination, filtres et schéma OpenAPI pour toutes les vues.
REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "PAGE_SIZE": 50,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "SteamLens API",
    "DESCRIPTION": "Données Steam agrégées, prêtes à tracer.",
    "VERSION": "0.1.0",
}

# Cache disque des réponses des API externes (backend/data/ est ignoré par git).
HOURS_PER_DAY = 24
SECONDS_PER_HOUR = 3600
HTTP_CACHE_DIR = BASE_DIR / "data" / "cache"
HTTP_CACHE_TTL_SECONDS = env.int("HTTP_CACHE_TTL_SECONDS", default=HOURS_PER_DAY * SECONDS_PER_HOUR)

# Le front Nuxt tourne sur le port 3000 en développement.
CORS_ALLOWED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
