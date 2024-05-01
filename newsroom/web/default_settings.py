import os
import pathlib
import tzlocal
import logging

from typing import Dict, List
from kombu import Queue, Exchange
from celery.schedules import crontab
from superdesk.default_settings import strtobool, env, local_to_utc_hour
from datetime import timedelta
from flask_babel import lazy_gettext

from superdesk.default_settings import (  # noqa
    VERSION,
    MONGO_URI,
    REDIS_URL,
    CONTENTAPI_MONGO_URI,
    CONTENTAPI_ELASTICSEARCH_URL,
    CONTENTAPI_ELASTICSEARCH_INDEX,
    CONTENTAPI_ELASTICSEARCH_SETTINGS,
    ELASTICSEARCH_URL,
    ELASTICSEARCH_SETTINGS,
    ELASTIC_DATE_FORMAT,
    CELERY_BROKER_URL,
    BROKER_URL,
    celery_queue,
    AMAZON_SECRET_ACCESS_KEY,
    AMAZON_ACCESS_KEY_ID,
    AMAZON_CONTAINER_NAME,
    AMAZON_OBJECT_ACL,
    AMAZON_S3_SUBFOLDER,
    AMAZON_REGION,
    MAIL_SERVER,
    MAIL_PORT,
    MAIL_USE_TLS,
    MAIL_USE_SSL,
    _MAIL_FROM,
    MAIL_USERNAME,
    MAIL_PASSWORD,
    CELERY_TASK_ALWAYS_EAGER,
    CELERY_TASK_SERIALIZER,
    CELERY_TASK_PROTOCOL,
    CELERY_TASK_IGNORE_RESULT,
    CELERY_TASK_SEND_EVENTS,
    CELERY_WORKER_DISABLE_RATE_LIMITS,
    CELERY_WORKER_TASK_SOFT_TIME_LIMIT,
    CELERY_WORKER_LOG_FORMAT,
    CELERY_WORKER_TASK_LOG_FORMAT,
    CELERY_WORKER_CONCURRENCY,
    CELERY_WORKER_PREFETCH_MULTIPLIER,
    CELERY_BEAT_SCHEDULE_FILENAME,
    LOG_CONFIG_FILE,
    SENTRY_DSN,
    CACHE_URL,
)

from newsroom.types import AuthProviderConfig, AuthProviderType

logger = logging.getLogger()

DEBUG = strtobool(os.environ.get("NEWSROOM_DEBUG", "false"))

# newsroom default db and index names
MONGO_DBNAME = env("MONGO_DBNAME", "newsroom")
# mongo
MONGO_URI = env("MONGO_URI", f"mongodb://localhost/{MONGO_DBNAME}")  # noqa
CONTENTAPI_MONGO_URI = env("CONTENTAPI_MONGO_URI", f"mongodb://localhost/{MONGO_DBNAME}")  # noqa
# elastic
ELASTICSEARCH_INDEX = env("ELASTICSEARCH_INDEX", MONGO_DBNAME)  # noqa
CONTENTAPI_ELASTICSEARCH_INDEX = env("CONTENTAPI_ELASTICSEARCH_INDEX", MONGO_DBNAME)  # noqa

# handle non-ascii characters by default
CONTENTAPI_ELASTICSEARCH_SETTINGS["settings"]["analysis"]["analyzer"]["html_field_analyzer"]["filter"] = [
    "lowercase",
    "asciifolding",
]

XML = False
IF_MATCH = True
JSON_SORT_KEYS = False
DOMAIN = {}

X_DOMAINS = "*"
X_MAX_AGE = 24 * 3600
X_HEADERS = [
    "Content-Type",
    "Accept",
    "If-Match",
    "Access-Control-Allow-Origin",
    "Authorization",
]
X_EXPOSE_HEADERS = ["Access-Control-Allow-Origin"]
X_ALLOW_CREDENTIALS = True
CACHE_CONTROL = "max-age=0, no-cache"  # disable caching api responses

URL_PREFIX = "api"

# keys for signing, should be binary
SECRET_KEY = os.environ.get("SECRET_KEY", "").encode()
if not SECRET_KEY:
    SECRET_KEY = b"E`<+\xa6\x1e\x02\xc5\x87\xfc\xd6\x87\x1f|\xf6\xbd\x0cK\x1a6\xff!\x97M\xc0\xc4\x11Ppg\xf7\xaa"
    logger.warning("SECRET_KEY is not set, hardcoded value is used instead. This should not be used on production!")

PUSH_KEY = os.environ.get("PUSH_KEY", "").encode()

#: Default TimeZone, will try to guess from server settings if not set
DEFAULT_TIMEZONE = os.environ.get("DEFAULT_TIMEZONE")

if DEFAULT_TIMEZONE is None:
    DEFAULT_TIMEZONE = tzlocal.get_localzone().zone

if not DEFAULT_TIMEZONE:
    raise ValueError("DEFAULT_TIMEZONE is empty")

BABEL_DEFAULT_TIMEZONE = DEFAULT_TIMEZONE

BLUEPRINTS = [
    "newsroom.wire",
    "newsroom.auth.views",
    "newsroom.users",
    "newsroom.companies",
    "newsroom.design",
    "newsroom.history",
    "newsroom.push",
    "newsroom.topics",
    "newsroom.upload",
    "newsroom.notifications",
    "newsroom.products",
    "newsroom.section_filters",
    "newsroom.navigations",
    "newsroom.cards",
    "newsroom.reports",
    "newsroom.public",
    "newsroom.agenda",
    "newsroom.settings",
    "newsroom.news_api.api_tokens",
    "newsroom.monitoring",
    "newsroom.oauth_clients",
    "newsroom.auth_server.oauth2",
    "newsroom.company_admin",
]

CORE_APPS = [
    "superdesk.notification",
    "superdesk.data_updates",
    "newsroom.wire.items",
    "content_api.search",
    "content_api.auth",
    "content_api.publish",
    "newsroom.users",
    "newsroom.auth.oauth",
    "newsroom.companies",
    "newsroom.wire",
    "newsroom.topics",
    "newsroom.upload",
    "newsroom.history",
    "newsroom.ui_config",
    "newsroom.notifications",
    "newsroom.products",
    "newsroom.section_filters",
    "newsroom.navigations",
    "newsroom.cards",
    "newsroom.reports",
    "newsroom.public",
    "newsroom.agenda",
    "newsroom.settings",
    "newsroom.photos",
    "newsroom.media_utils",
    "newsroom.news_api",
    "newsroom.news_api.api_tokens",
    "newsroom.news_api.api_audit",
    "newsroom.monitoring",
    "newsroom.company_expiry_alerts",
    "newsroom.oauth_clients",
    "newsroom.auth_server.client",
    "newsroom.email_templates",
    "newsroom.company_admin",
    "newsroom.search",
    "newsroom.notifications.send_scheduled_notifications",
]

SITE_NAME = "Newshub"
COPYRIGHT_HOLDER = "Sourcefabric"
COPYRIGHT_NOTICE = ""
USAGE_TERMS = ""
CONTACT_ADDRESS = "#"
PRIVACY_POLICY = "#"
TERMS_AND_CONDITIONS = "#"
SHOW_COPYRIGHT = True
SHOW_USER_REGISTER = False

TEMPLATES_AUTO_RELOAD = True

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S+0000"

WEBPACK_ASSETS_URL = os.environ.get("WEBPACK_ASSETS_URL")
WEBPACK_SERVER_URL = os.environ.get("WEBPACK_SERVER_URL")

# How many days a new account can stay active before it is approved by admin
NEW_ACCOUNT_ACTIVE_DAYS = 14

# Enable CSRF protection for forms
WTF_CSRF_ENABLED = True

#: The number of days a token is valid
RESET_PASSWORD_TOKEN_TIME_TO_LIVE = 7
#: The number of days a validation token is valid
VALIDATE_ACCOUNT_TOKEN_TIME_TO_LIVE = 7
#: The number login attempts allowed before account is locked
MAXIMUM_FAILED_LOGIN_ATTEMPTS = 5
#: default sender for superdesk emails
MAIL_DEFAULT_SENDER = _MAIL_FROM or "newsroom@localhost"
# Recipients for the sign up form filled by new users (single or comma separated)
SIGNUP_EMAIL_RECIPIENTS = os.environ.get("SIGNUP_EMAIL_RECIPIENTS")

#: public client url - used to create links within emails etc
CLIENT_URL = os.environ.get("CLIENT_URL", "http://localhost:5050")
PREFERRED_URL_SCHEME = os.environ.get("PREFERRED_URL_SCHEME") or ("https" if "https://" in CLIENT_URL else "http")

MEDIA_PREFIX = os.environ.get("MEDIA_PREFIX", "/assets")

# Flask Limiter Settings
RATELIMIT_ENABLED = True
RATELIMIT_STRATEGY = "fixed-window"

# Cache Settings
# https://flask-caching.readthedocs.io/en/latest/#configuring-flask-caching
CACHE_TYPE = os.environ.get("CACHE_TYPE", "simple")  # in-memory cache
# The default timeout that is used if no timeout is specified in sec
CACHE_DEFAULT_TIMEOUT = 3600
# Redis host (used only if CACHE_TYPE is redis)
CACHE_REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")

# Recaptcha Settings
RECAPTCHA_PUBLIC_KEY = os.environ.get("RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = os.environ.get("RECAPTCHA_PRIVATE_KEY")

# Filter tab behaviour
# If true, aggregations will be against all content all the time
# If false, aggregations will change by filters applied
FILTER_BY_POST_FILTER = False

FILTER_AGGREGATIONS = True

# List of filters to remove matching stories when news only switch is turned on
NEWS_ONLY_FILTERS = [
    {"match": {"genre.code": "Results (sport)"}},
    {"match": {"source": "PMF"}},
]

# avoid conflict with superdesk
SESSION_COOKIE_NAME = "newsroom_session"

# the lifetime of a permanent session in seconds
PERMANENT_SESSION_LIFETIME = 604800  # 7 days

# the time to live value in days for user notifications
NOTIFICATIONS_TTL = 1

SERVICES = [
    {"name": "Domestic Sport", "code": "t"},
    {"name": "Overseas Sport", "code": "s"},
    {"name": "Finance", "code": "f"},
    {"name": "International News", "code": "i"},
    {"name": "Entertainment", "code": "e"},
    # {"name": "Australian General News", "code": "a"},
    # {"name": "Australian Weather", "code": "b"},
    # {"name": "General Features", "code": "c"},
    # {"name": "FormGuide", "code": "h"},
    # {"name": "Press Release Service", "code": "j"},
    # {"name": "Lotteries", "code": "l"},
    # {"name": "Line Check Messages", "code": "m"},
    # {"name": "State Parliaments", "code": "o"},
    # {"name": "Federal Parliament", "code": "p"},
    # {"name": "Stockset", "code": "q"},
    # {"name": "Racing (Turf)", "code": "r"},
    # {"name": "Advisories", "code": "v"},
    # {"name": "Special Events (olympics/ Aus elections)", "code": "x"},
]


# Hides or displays abstract on preview panel and details modal
DISPLAY_ABSTRACT = False

WATERMARK_IMAGE = None  # os.path.join(os.path.dirname(__file__), '../static', 'watermark.png')

GOOGLE_MAPS_KEY = os.environ.get("GOOGLE_MAPS_KEY")
GOOGLE_ANALYTICS = os.environ.get("GOOGLE_ANALYTICS")

COVERAGE_TYPES = {
    "text": {"name": lazy_gettext("Text"), "icon": "text"},
    "photo": {"name": lazy_gettext("Photo"), "icon": "photo"},
    "picture": {"name": lazy_gettext("Picture"), "icon": "photo"},
    "audio": {"name": lazy_gettext("Audio"), "icon": "audio"},
    "video": {"name": lazy_gettext("Video"), "icon": "video"},
    "explainer": {"name": lazy_gettext("Explainer"), "icon": "explainer"},
    "infographics": {"name": lazy_gettext("Infographics"), "icon": "infographics"},
    "graphic": {"name": lazy_gettext("Graphic"), "icon": "infographics"},
    "live_video": {"name": lazy_gettext("Live Video"), "icon": "live-video"},
    "live_blog": {"name": lazy_gettext("Live Blog"), "icon": "live-blog"},
    "video_explainer": {"name": lazy_gettext("Video Explainer"), "icon": "explainer"},
}

LANGUAGES = ["en", "fi", "fr_CA"]
DEFAULT_LANGUAGE = "en"

CLIENT_LOCALE_FORMATS = {
    "en": {  # defaults
        "TIME_FORMAT": "HH:mm",
        "DATE_FORMAT": "DD/MM/YYYY",
        "COVERAGE_DATE_TIME_FORMAT": "HH:mm DD/MM",
        "COVERAGE_DATE_FORMAT": "DD/MM",
        "DATE_FORMAT_HEADER": "EEEE, dd/MM/yyyy",
        "NOTIFICATION_EMAIL_TIME_FORMAT": "HH:mm a",
        "NOTIFICATION_EMAIL_DATE_FORMAT": "MMMM d, yyyy",
        "NOTIFICATION_EMAIL_DATETIME_FORMAT": "HH:mm a MMMM d, yyyy",
    },
    "fr_CA": {  # example - you can overwrite any format above
        "DATE_FORMAT": "DD/MM/YYYY",
        "DATE_FORMAT_HEADER": "EEEE, 'le' d MMMM yyyy",
        "NOTIFICATION_EMAIL_TIME_FORMAT": "HH:mm",
        "NOTIFICATION_EMAIL_DATE_FORMAT": "MMMM d, yyyy",
        "NOTIFICATION_EMAIL_DATETIME_FORMAT": "HH:mm MMMM d, yyyy",
    },
}

#: Default times for scheduled topic notifications
#:
#: .. versionadded: 2.5.0
#:
DEFAULT_SCHEDULED_NOTIFICATION_TIMES = [
    "07:00",
    "15:00",
    "19:00",
]

# Client configuration
CLIENT_CONFIG = {
    "debug": DEBUG,
    "default_language": DEFAULT_LANGUAGE,
    "locale_formats": CLIENT_LOCALE_FORMATS,
    "coverage_types": COVERAGE_TYPES,
    "list_animations": True,  # Enables or disables the animations for list item select boxes,
    "display_news_only": True,  # Displays news only switch in wire,
    "display_agenda_featured_stories_only": True,  # Displays top/featured stories switch in agenda,
    "default_timezone": DEFAULT_TIMEZONE,
    "item_actions": {},
    "display_abstract": DISPLAY_ABSTRACT,
    "display_credits": False,
    "filter_panel_defaults": {
        "tab": {
            "wire": "nav",  # Options are 'nav', 'topics', 'filters'
            "agenda": "nav",
        },
        "open": {
            "wire": False,
            "agenda": False,
        },
    },
    "advanced_search": {
        "fields": {
            "wire": ["headline", "slugline", "body_html"],
            "agenda": ["name", "headline", "slugline", "description"],
        },
    },
    "scheduled_notifications": {"default_times": DEFAULT_SCHEDULED_NOTIFICATION_TIMES},
    "coverage_status_filter": {
        "not planned": {
            "enabled": True,
            "index": 1,
            "option_label": lazy_gettext("No Coverage"),
            "button_label": lazy_gettext("No Coverage"),
        },
        "planned": {
            "enabled": True,
            "index": 2,
            "option_label": lazy_gettext("Is Planned"),
            "button_label": lazy_gettext("Is Planned"),
        },
        "may be": {
            "enabled": True,
            "index": 3,
            "option_label": lazy_gettext("Not Decided / On request"),
            "button_label": lazy_gettext("Not Decided / On Request"),
        },
        "not intended": {
            "enabled": True,
            "index": 4,
            "option_label": lazy_gettext("Not Intended / Cancelled"),
            "button_label": lazy_gettext("Not Intended / Cancelled"),
        },
        "completed": {
            "enabled": True,
            "index": 5,
            "option_label": lazy_gettext("Completed"),
            "button_label": lazy_gettext("Completed"),
        },
    },
}

# Enable rendering of the date in the base view
SHOW_DATE = True

# Enable iframely support for item body_html
IFRAMELY = True

COMPANY_TYPES = []

#: celery config
CELERY_WORKER_TASK_TIME_LIMIT = 600

WEBSOCKET_EXCHANGE = celery_queue("newsroom_notification")

CELERY_TASK_DEFAULT_QUEUE = celery_queue("newsroom")
CELERY_TASK_QUEUES = (
    Queue(
        celery_queue("newsroom"),
        Exchange(celery_queue("newsroom"), type="topic"),
        routing_key="newsroom.#",
    ),
    Queue(
        celery_queue("newsroom.push"),
        Exchange(celery_queue("newsroom.push")),
        routing_key="newsroom.push",
    ),
)

CELERY_TASK_ROUTES = {
    "newsroom.push.*": {
        "queue": celery_queue("newsroom.push"),
        "routing_key": "newsroom.push",
    },
    "newsroom.*": {
        "queue": celery_queue("newsroom"),
        "routing_key": "newsroom.task",
    },
}


#: celery beat config
CELERY_BEAT_SCHEDULE = {
    "newsroom:company_expiry": {
        "task": "newsroom.company_expiry_alerts.company_expiry",
        "schedule": crontab(hour=local_to_utc_hour(0), minute=0),  # Runs every day at midnight
    },
    "newsroom:monitoring_schedule_alerts": {
        "task": "newsroom.monitoring.email_alerts.monitoring_schedule_alerts",
        "schedule": timedelta(seconds=60),
        "options": {"expires": 59},  # if the task is not executed within 59 seconds, it will be discarded
    },
    "newsroom:monitoring_immediate_alerts": {
        "task": "newsroom.monitoring.email_alerts.monitoring_immediate_alerts",
        "schedule": timedelta(seconds=60),
        "options": {"expires": 59},  # if the task is not executed within 59 seconds, it will be discarded
    },
    "newsroom:remove_expired_content_api": {
        "task": "content_api.commands.item_expiry",
        "schedule": crontab(hour=local_to_utc_hour(2), minute=0),  # Runs every day at 2am
    },
    "newsroom:remove_expired_agenda": {
        "task": "newsroom.commands.async_remove_expired_agenda",
        "schedule": crontab(hour=local_to_utc_hour(3), minute=0),  # Runs every day at 3am
    },
    "newsroom:send_scheduled_notifications": {
        "task": "newsroom.notifications.send_scheduled_notifications.send_scheduled_notifications",
        "schedule": crontab(minute="*/5"),
        "options": {"expires": 5 * 60 - 1},
    },
}

MAX_EXPIRY_QUERY_LIMIT = os.environ.get("MAX_EXPIRY_QUERY_LIMIT", 100)
CONTENT_API_EXPIRY_DAYS = os.environ.get("CONTENT_API_EXPIRY_DAYS", 180)

NEWS_API_ENABLED = strtobool(env("NEWS_API_ENABLED", "false"))

# Enables the application of product filtering to image references in the API and ATOM responses
NEWS_API_IMAGE_PERMISSIONS_ENABLED = strtobool(env("NEWS_API_IMAGE_PERMISSIONS_ENABLED", "false"))

ELASTICSEARCH_SETTINGS.setdefault("settings", {})["query_string"] = {
    # https://discuss.elastic.co/t/configuring-the-standard-tokenizer/8691/5
    "analyze_wildcard": False
}

# count above 10k
ELASTICSEARCH_TRACK_TOTAL_HITS = True

ELASTICSEARCH_FIX_QUERY = False

#: server working directory
#: should be set in settings.py
SERVER_PATH = pathlib.Path(__file__).resolve().parent.parent

#: client working directory
#: used to locate client/dist/manifest.json file
CLIENT_PATH = SERVER_PATH

#: path to app specific translations
TRANSLATIONS_PATH = None

#: server date/time formats
#: defined using babel syntax http://babel.pocoo.org/en/latest/dates.html#date-and-time
TIME_FORMAT_SHORT = "HH:mm"
DATE_FORMAT_SHORT = "short"
DATE_FORMAT_HEADER = "EEEE, dd/MM/yyyy"
DATETIME_FORMAT_SHORT = "short"
DATETIME_FORMAT_LONG = "dd/MM/yyyy HH:mm"
AGENDA_EMAIL_LIST_DATE_FORMAT = "HH:mm (dd/MM/yyyy)"

PREPEND_EMBARGOED_TO_WIRE_SEARCH = False

#: allow embargoed items on dashboard
DASHBOARD_EMBARGOED = True

#: OAuth settings
AUTH_SERVER_EXPIRATION_DELAY = env("AUTH_SERVER_EXPIRATION_TIME", 60 * 60 * 4)  # 4 hours by default
AUTH_SERVER_SHARED_SECRET = env("AUTH_SERVER_SHARED_SECRET", "")

#: Google OAuth Settings
#:
#: .. versionadded:: 2.1
#:
GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = env("GOOGLE_CLIENT_SECRET")
GOOGLE_LOGIN = True


#: Elastic APM
#:
#: .. versionadded:: 2.0.1
#:
APM_SERVER_URL = env("APM_SERVER_URL")
APM_SECRET_TOKEN = env("APM_SECRET_TOKEN")
APM_SERVICE_NAME = env("APM_SERVICE_NAME") or SITE_NAME

#: Filter out subjects with schema which is not in the whitelist
#: before storing the item to avoid those being displayed in filter,
#: preview and outputs.
#:
#: .. versionadded:: 2.1
#:
WIRE_SUBJECT_SCHEME_WHITELIST = []

#: Agenda Filter groups (defaults set in ``newsroom.agenda.init_app``)
#:
#: .. versionadded:: 2.1.0
#:
AGENDA_GROUPS = None

#: If True, allows Users to log in after their associated Company has expired
#:
#: .. versionadded:: 2.1.0
#:
ALLOW_EXPIRED_COMPANY_LOGINS = False

#: The timeout used on the cache for the dashboard items
#:
#: .. versionadded:: 2.1.0
#:
DASHBOARD_CACHE_TIMEOUT = 300

#: If True, deletes all Dashboard item caches when new items are pushed
#:
#: .. versionadded:: 2.1.0
#:
DELETE_DASHBOARD_CACHE_ON_PUSH = True

#: Path to SAML config
#:
#: .. versionadded:: 2.3
#:
SAML_PATH = os.environ.get("SAML_PATH") or ""

#: Company name which will be assigned to newsly created users
#:
#: .. versionadded:: 2.3
#:
SAML_COMPANY = ""

#: Button label displayed on the login page
#:
#: .. versionadded:: 2.3
#:
SAML_LABEL = "SSO"

#: List of available configs for SAML, there should be a folder inside SAML_BASE_PATH for each.
#:
#: .. versionadded:: 2.5
#:
SAML_CLIENTS: List[str] = []

#: Base path for SAML_COMPANIES config
#:
#: .. versionadded:: 2.5
#:
SAML_BASE_PATH: str = os.environ.get("SAML_BASE_PATH") or ""

#: Mapping SAML claims to user data fields.
#:
#: .. versionadded:: 2.5
#:
SAML_USER_MAPPING = {
    "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname": "first_name",
    "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname": "last_name",
}

#: Rebuild elastic mapping on ``initialize_data`` mapping error
#:
#: .. versionadded:: 2.3
#:
REBUILD_ELASTIC_ON_INIT_DATA_ERROR = strtobool(env("REBUILD_ELASTIC_ON_INIT_DATA_ERROR", "true"))

#: The number of days before Agenda items are removed. Defaults to 0 which means no purging occurs
#:
#: .. versionadded:: 2.3
#:
AGENDA_EXPIRY_DAYS = int(env("AGENDA_EXPIRY_DAYS", 0))

#: The maximum number of days allowed for an Event's duration
#:
#: .. versionadded:: 2.3.2
#:
MAX_MULTI_DAY_EVENT_DURATION = int(env("MAX_MULTI_DAY_EVENT_DURATION", 365))

#:
#:
#: .. versionadded: 2.4.0
#:
DEFAULT_ALLOW_COMPANIES_TO_MANAGE_PRODUCTS = False

#:
#:
#:
HOME_SECTION = lazy_gettext("Home")

#:
#: .. versionadded: 2.5.0
#:
WIRE_SECTION = lazy_gettext("Wire")

#:
#: .. versionadded: 2.5.0
#:
AGENDA_SECTION = lazy_gettext("Agenda")

#:
#: .. versionadded: 2.5.0
#:
MONITORING_SECTION = lazy_gettext("Monitoring")

#:
#: .. versionadded: 2.5.0
#:
SAVED_SECTION = lazy_gettext("Saved / Watched")

#:
#: .. versionadded: 2.5.0
#:
WIRE_SEARCH_FIELDS = [
    "slugline",
    "headline",
    "byline",
    "body_html",
    "body_text",
    "description_html",
    "description_text",
    "keywords",
    "located",
]

#:
#: .. versionadded: 2.5.0
#:
AGENDA_SEARCH_FIELDS = [
    "name",
    "slugline",
    "headline",
    "definition_short",
    "definition_long",
    "description_text",
    "location.name",
]


#: The available authentication providers
#:
#: .. versionadded:: 2.5.0
#:
AUTH_PROVIDERS: List[AuthProviderConfig] = [
    {
        "_id": "newshub",
        "name": lazy_gettext("Newshub"),
        "auth_type": AuthProviderType.PASSWORD,
    }
]

FIREBASE_CLIENT_CONFIG = {
    "apiKey": env("FIREBASE_API_KEY"),
    "authDomain": env("FIREBASE_AUTH_DOMAIN"),
    "projectId": env("FIREBASE_PROJECT_ID"),
    "messagingSenderId": env("FIREBASE_SENDER_ID"),
}

FIREBASE_ENABLED = bool(FIREBASE_CLIENT_CONFIG["apiKey"] and FIREBASE_CLIENT_CONFIG["authDomain"])

#:
#: If `True` it will show multi day events only on starting day,
#: when `False` those will be visible on every day.
#:
#: .. versionadded: 2.5.0
#:
AGENDA_SHOW_MULTIDAY_ON_START_ONLY = True

#: Send email notifications for corrections of wire items
#:
#:
#: .. versionadded: 2.5.0
#:
WIRE_NOTIFICATIONS_ON_CORRECTIONS = False

#: Set source specific expiry
#:
#: .. versionadded: 2.6
#:
SOURCE_EXPIRY_DAYS: Dict[str, int] = {}

#: If `True` will enable the Public Dashboard feature
#:
#: .. versionadded: 2.6
#:
PUBLIC_DASHBOARD = False

#: The timeout used on the content cache for public pages
#:
#: .. versionadded: 2.6
#:
PUBLIC_CONTENT_CACHE_TIMEOUT = 240

#: List of Wire item fields to keep when accessing from public dashboard
#:
#: .. versionadded: 2.6
#:
PUBLIC_WIRE_ALLOWED_FIELDS = [
    "_id",
    "guid",
    "type",
    "slugline",
    "headline",
    "anpa_take_key",
    "description_html",
    "description_text",
    "abstract",
    "body_html",
    "source",
    "versioncreated",
    "wordcount",
    "charcount",
    "byline",
    "copyrightnotice",
    "language",
    "mimetype",
    "priority",
    "urgency",
    "usageterms",
    "version",
    "renditions",
]

#: Filter subject based on this config in the Formatter

AGENDA_CSV_SUBJECT_SCHEMES = []

#: Language to Email Sender map
#: When sending an email, the system will attempt to use the sender from this map
#: based on the language from the user profile, falling back to ``MAIL_DEFAULT_SENDER`` if not found
#:
#: .. versionadded: 2.6.0
#:
EMAIL_DEFAULT_SENDER_NAME = None
EMAIL_SENDER_NAME_LANGUAGE_MAP = {}

#: Hides Coverage assignee details for public users, such as desk and user details
#:
#: .. versionadded: 2.7
#:
AGENDA_HIDE_COVERAGE_ASSIGNEES = False
