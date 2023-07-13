import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__name__))

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# https://docs.djangoproject.com/en/3.2/releases/3.2/#customizing-type-of-auto-created-primary-keys
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "nbv58c^&b8-095(^)&_BV98596v)&CX#^$&%*^V5"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# To allow debug in template context
# https://docs.djangoproject.com/en/3.1/ref/settings/#internal-ips
INTERNAL_IPS = ["127.0.0.1"]

# Application definition

INSTALLED_APPS = [
    # "maintenance_mode",  # this has to be first if enabled
    "django.contrib.admin",
    "hijack",
    "hijack.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.postgres",
    "django_rq",
    "django_bleach",
    "django_jsonform",
    "tz_detect",
    "sass_processor",
    "auditlog",
    "markdownx",
    "polymorphic",
    "easy_thumbnails",
    "user_messages",
    "fontawesomefree",
    # "anymail",
    # "silk",
]

INSTALLED_APPS += [
    "management.apps.ManagementConfig",
    "mastodon.apps.MastodonConfig",
    "common.apps.CommonConfig",
    "users.apps.UsersConfig",
    "catalog.apps.CatalogConfig",
    "journal.apps.JournalConfig",
    "social.apps.SocialConfig",
    "developer.apps.DeveloperConfig",
    "legacy.apps.LegacyConfig",
]

INSTALLED_APPS += [  # we may override templates in these 3rd party apps
    "oauth2_provider",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # "silk.middleware.SilkyMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "oauth2_provider.middleware.OAuth2TokenMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "hijack.middleware.HijackUserMiddleware",
    "tz_detect.middleware.TimezoneMiddleware",
    "auditlog.middleware.AuditlogMiddleware",
    # "maintenance_mode.middleware.MaintenanceModeMiddleware",  # this should be last if enabled
]

ROOT_URLCONF = "boofilsic.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                # "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                # 'django.contrib.messages.context_processors.messages',
                "user_messages.context_processors.messages",
                "boofilsic.context_processors.site_info",
            ],
        },
    },
]

WSGI_APPLICATION = "boofilsic.wsgi.application"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_NAME", "test"),
            "USER": os.environ.get("DB_USER", "postgres"),
            "PASSWORD": os.environ.get("DB_PASSWORD", "admin123"),
            "HOST": os.environ.get("DB_HOST", "127.0.0.1"),
            "OPTIONS": {
                "client_encoding": "UTF8",
                # 'isolation_level': psycopg2.extensions.ISOLATION_LEVEL_DEFAULT,
            },
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "boofilsic",
            "USER": "doubaniux",
            "PASSWORD": "password",
            "HOST": "localhost",
            "OPTIONS": {
                "client_encoding": "UTF8",
                # 'isolation_level': psycopg2.extensions.ISOLATION_LEVEL_DEFAULT,
            },
        }
    }

# Customized auth backend, glue OAuth2 and Django User model together
# https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#authentication-backends

AUTHENTICATION_BACKENDS = [
    "mastodon.auth.OAuth2Backend",
    "oauth2_provider.backends.OAuth2Backend",
]


MARKDOWNX_MARKDOWNIFY_FUNCTION = "journal.renderers.render_md"


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "zh-hans"

TIME_ZONE = "Asia/Shanghai"

USE_I18N = True

USE_L10N = True

USE_TZ = True


if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_PRELOAD = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "{levelname} {asctime} {name}:{lineno} {message}",
                "style": "{",
            },
        },
        "handlers": {
            "file": {
                "level": "INFO",
                "class": "logging.FileHandler",
                "filename": os.path.join(BASE_DIR, "log"),
                "formatter": "simple",
            },
        },
        "root": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": True,
        },
    }

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static/")

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "sass_processor.finders.CssFinder",
]

AUTH_USER_MODEL = "users.User"

SILENCED_SYSTEM_CHECKS = [
    "admin.E404",  # Required by django-user-messages
]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media/")

SITE_INFO = {
    "site_name": os.environ.get("APP_NAME", "NiceDB"),
    "site_url": os.environ.get("APP_URL", "https://nicedb.org"),
    "support_link": "https://github.com/doubaniux/boofilsic/issues",
    "social_link": "https://donotban.com/@testie",
    "donation_link": "https://patreon.com/tertius",
    "version_hash": None,
    "settings_module": os.getenv("DJANGO_SETTINGS_MODULE"),
    "sentry_dsn": None,
}

REDIRECT_URIS = SITE_INFO["site_url"] + "/users/OAuth2_login/"
# if you are creating new site, use
# REDIRECT_URIS = SITE_INFO["site_url"] + "/account/login/oauth"


# Path to save report related images, ends with slash
REPORT_MEDIA_PATH_ROOT = "report/"
MARKDOWNX_MEDIA_PATH = "review/"
BOOK_MEDIA_PATH_ROOT = "book/"
DEFAULT_BOOK_IMAGE = os.path.join(BOOK_MEDIA_PATH_ROOT, "default.svg")
MOVIE_MEDIA_PATH_ROOT = "movie/"
DEFAULT_MOVIE_IMAGE = os.path.join(MOVIE_MEDIA_PATH_ROOT, "default.svg")
SONG_MEDIA_PATH_ROOT = "song/"
DEFAULT_SONG_IMAGE = os.path.join(SONG_MEDIA_PATH_ROOT, "default.svg")
ALBUM_MEDIA_PATH_ROOT = "album/"
DEFAULT_ALBUM_IMAGE = os.path.join(ALBUM_MEDIA_PATH_ROOT, "default.svg")
GAME_MEDIA_PATH_ROOT = "game/"
DEFAULT_GAME_IMAGE = os.path.join(GAME_MEDIA_PATH_ROOT, "default.svg")
COLLECTION_MEDIA_PATH_ROOT = "collection/"
DEFAULT_COLLECTION_IMAGE = os.path.join(COLLECTION_MEDIA_PATH_ROOT, "default.svg")
SYNC_FILE_PATH_ROOT = "sync/"
EXPORT_FILE_PATH_ROOT = "export/"

# Allow user to login via any Mastodon/Pleroma sites
ALLOW_ANY_SITE = False

# Allow user to create account with email (and link to Mastodon account later)
ALLOW_EMAIL_ONLY_ACCOUNT = False

# Timeout of requests to Mastodon, in seconds
MASTODON_TIMEOUT = 30

MASTODON_CLIENT_SCOPE = "read write follow"
# use the following if it's a new site
# MASTODON_CLIENT_SCOPE = 'read:accounts read:follows read:search read:blocks read:mutes write:statuses write:media'

MASTODON_LEGACY_CLIENT_SCOPE = "read write follow"

# Emoji code in mastodon
STAR_SOLID = ":star_solid:"
STAR_HALF = ":star_half:"
STAR_EMPTY = ":star_empty:"

# Default redirect loaction when access login required view
LOGIN_URL = "/account/login"

# Admin site root url
ADMIN_URL = "tertqX7256n7ej8nbv5cwvsegdse6w7ne5rHd"

SCRAPING_TIMEOUT = 90

# ScraperAPI api key
SCRAPERAPI_KEY = "***REMOVED***"
PROXYCRAWL_KEY = None
SCRAPESTACK_KEY = None

# Spotify credentials
SPOTIFY_CREDENTIAL = "***REMOVED***"

# IMDb API service https://imdb-api.com/
IMDB_API_KEY = "***REMOVED***"

# The Movie Database (TMDB) API Keys
TMDB_API3_KEY = "***REMOVED***"
# TMDB_API4_KEY = "deadbeef.deadbeef.deadbeef"

# Google Books API Key
GOOGLE_API_KEY = "***REMOVED***"

# Discogs API Key
# How to get: a personal access token from https://www.discogs.com/settings/developers
DISCOGS_API_KEY = "***REMOVED***"

# IGDB
IGDB_CLIENT_ID = "deadbeef"
IGDB_CLIENT_SECRET = "deadbeef"

BLEACH_STRIP_COMMENTS = True
BLEACH_STRIP_TAGS = True

# Thumbnail setting
# It is possible to optimize the image size even more: https://easy-thumbnails.readthedocs.io/en/latest/ref/optimize/
THUMBNAIL_ALIASES = {
    "": {
        "normal": {
            "size": (200, 200),
            "crop": "scale",
            "autocrop": True,
        },
    },
}
# THUMBNAIL_PRESERVE_EXTENSIONS = ('svg',)
if DEBUG:
    THUMBNAIL_DEBUG = True

# https://django-debug-toolbar.readthedocs.io/en/latest/
# maybe benchmarking before deployment

REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")

RQ_QUEUES = {
    "mastodon": {
        "HOST": REDIS_HOST,
        "PORT": 6379,
        "DB": 0,
        "DEFAULT_TIMEOUT": -1,
    },
    "export": {
        "HOST": REDIS_HOST,
        "PORT": 6379,
        "DB": 0,
        "DEFAULT_TIMEOUT": -1,
    },
    "import": {
        "HOST": "localhost",
        "PORT": 6379,
        "DB": 0,
        "DEFAULT_TIMEOUT": -1,
    },
    "fetch": {
        "HOST": "localhost",
        "PORT": 6379,
        "DB": 0,
        "DEFAULT_TIMEOUT": -1,
    },
    "crawl": {
        "HOST": "localhost",
        "PORT": 6379,
        "DB": 0,
        "DEFAULT_TIMEOUT": -1,
    },
    "doufen": {
        "HOST": REDIS_HOST,
        "PORT": 6379,
        "DB": 0,
        "DEFAULT_TIMEOUT": -1,
    },
}

RQ_SHOW_ADMIN_LINK = True

SEARCH_INDEX_NEW_ONLY = False


# SEARCH_BACKEND = 'MEILISEARCH'
# MEILISEARCH_SERVER = 'http://127.0.0.1:7700'
# MEILISEARCH_KEY = 'deadbeef'

# SEARCH_BACKEND = "TYPESENSE"
# TYPESENSE_CONNECTION = {
#    "api_key": "xyz",
#    "nodes": [{"host": "localhost", "port": "8108", "protocol": "http"}],
#    "connection_timeout_seconds": 2,
# }

SEARCH_BACKEND = None

DOWNLOADER_RETRIES = 3
DOWNLOADER_SAVEDIR = None
DISABLE_MODEL_SIGNAL = False  # disable index and social feeds during importing/etc

# MAINTENANCE_MODE = False
# MAINTENANCE_MODE_IGNORE_ADMIN_SITE = True
# MAINTENANCE_MODE_IGNORE_SUPERUSER = True
# MAINTENANCE_MODE_IGNORE_ANONYMOUS_USER = True
# MAINTENANCE_MODE_IGNORE_URLS = (r"^/users/connect/", r"^/users/OAuth2_login/")

# SILKY_AUTHENTICATION = True  # User must login
# SILKY_AUTHORISATION = True  # User must have permissions
# SILKY_PERMISSIONS = lambda user: user.is_superuser
# SILKY_MAX_RESPONSE_BODY_SIZE = 1024  # If response body>1024 bytes, ignore
# SILKY_INTERCEPT_PERCENT = 10

DISCORD_WEBHOOKS = {}

NINJA_PAGINATION_PER_PAGE = 20
OAUTH2_PROVIDER = {
    "ACCESS_TOKEN_EXPIRE_SECONDS": 3600 * 24 * 365,
    "PKCE_REQUIRED": False,
}
OAUTH2_PROVIDER_APPLICATION_MODEL = "developer.Application"

DEVELOPER_CONSOLE_APPLICATION_CLIENT_ID = "NEODB_DEVELOPER_CONSOLE"
