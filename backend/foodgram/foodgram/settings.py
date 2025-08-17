import os
from pathlib import Path

from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")

DEBUG = False

ALLOWED_HOSTS = [
    "89.169.181.37",  # ваш публичный IP
    "backend",  # имя сервиса в docker-compose
    "localhost",  # для локальной разработки
    "127.0.0.1",  # для локальной разработки
    "andrievskis.sytes.net",  # личный домен
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


INTERNAL_IPS = ["127.0.0.1", "backend"]  # для отладки  # для отладки в Docker

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "djoser",
    "sorl.thumbnail",
    "django_filters",
    "ingredients.apps.IngredientsConfig",
    "recipes.apps.RecipesConfig",
    "tags.apps.TagsConfig",
    "users.apps.UsersConfig",
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


ROOT_URLCONF = "foodgram.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "foodgram.wsgi.application"

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": "db.sqlite3",
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "foodgram"),
        "USER": os.getenv("POSTGRES_USER", "foodgram_user"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "foodgram_password"),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME":
            "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME":
            "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME":
            "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "ru"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True
USE_L10N = True
USE_TZ = True


STATIC_URL = "/django-static/"
STATIC_ROOT = "/app/static"

MEDIA_URL = "/media/"
MEDIA_ROOT = "/app/media"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "SEARCH_PARAM": "name",
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",  # ✅ Для загрузки файлов
    ],
}


DJOSER = {
    "LOGIN_FIELD": "email",
    "SERIALIZERS": {
        "user_create": "users.serializers.CustomUserCreateSerializer",
        "user": "users.serializers.CustomUserSerializer",
        "current_user": "users.serializers.CustomUserSerializer",
    },
}
CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r"^/api/.*$"
