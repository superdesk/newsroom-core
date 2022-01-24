import os
import pathlib
import tzlocal
import logging

from kombu import Queue, Exchange
from celery.schedules import crontab
from superdesk.default_settings import strtobool, env, local_to_utc_hour
from datetime import timedelta

from superdesk.default_settings import ( # noqa
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
    CELERY_BEAT_SCHEDULE_FILENAME,
    LOG_CONFIG_FILE,
    SENTRY_DSN,
)

logger = logging.getLogger()

DEBUG = strtobool(os.environ.get('NEWSROOM_DEBUG', 'false'))

# newsroom default db and index names
MONGO_DBNAME = env('MONGO_DBNAME', 'newsroom')
# mongo
MONGO_URI = env('MONGO_URI', f'mongodb://localhost/{MONGO_DBNAME}') # noqa
CONTENTAPI_MONGO_URI = env('CONTENTAPI_MONGO_URI', f'mongodb://localhost/{MONGO_DBNAME}') # noqa
# elastic
ELASTICSEARCH_INDEX = env('ELASTICSEARCH_INDEX', MONGO_DBNAME) # noqa
CONTENTAPI_ELASTICSEARCH_INDEX = env('CONTENTAPI_ELASTICSEARCH_INDEX', MONGO_DBNAME) # noqa

XML = False
IF_MATCH = True
JSON_SORT_KEYS = False
DOMAIN = {}

X_DOMAINS = '*'
X_MAX_AGE = 24 * 3600
X_HEADERS = ['Content-Type', 'Accept', 'If-Match', 'Access-Control-Allow-Origin', 'Authorization']
X_EXPOSE_HEADERS = ['Access-Control-Allow-Origin']
X_ALLOW_CREDENTIALS = True

URL_PREFIX = 'api'

# keys for signing, should be binary
SECRET_KEY = os.environ.get('SECRET_KEY', '').encode()
if not SECRET_KEY:
    SECRET_KEY = b'E`<+\xa6\x1e\x02\xc5\x87\xfc\xd6\x87\x1f|\xf6\xbd\x0cK\x1a6\xff!\x97M\xc0\xc4\x11Ppg\xf7\xaa'
    logger.warning('SECRET_KEY is not set, hardcoded value is used instead. This should not be used on production!')

PUSH_KEY = os.environ.get('PUSH_KEY', '').encode()

#: Default TimeZone, will try to guess from server settings if not set
DEFAULT_TIMEZONE = os.environ.get('DEFAULT_TIMEZONE')

if DEFAULT_TIMEZONE is None:
    DEFAULT_TIMEZONE = tzlocal.get_localzone().zone

if not DEFAULT_TIMEZONE:
    raise ValueError("DEFAULT_TIMEZONE is empty")

BABEL_DEFAULT_TIMEZONE = DEFAULT_TIMEZONE

BLUEPRINTS = [
    'newsroom.wire',
    'newsroom.auth',
    'newsroom.users',
    'newsroom.companies',
    'newsroom.design',
    'newsroom.history',
    'newsroom.push',
    'newsroom.topics',
    'newsroom.upload',
    'newsroom.notifications',
    'newsroom.products',
    'newsroom.section_filters',
    'newsroom.navigations',
    'newsroom.cards',
    'newsroom.reports',
    'newsroom.public',
    'newsroom.agenda',
    'newsroom.settings',
    'newsroom.news_api.api_tokens',
    'newsroom.monitoring',
    'newsroom.oauth_clients',
    'newsroom.auth_server.oauth2',
]

CORE_APPS = [
    'superdesk.notification',
    'superdesk.data_updates',
    'content_api.items',
    'content_api.items_versions',
    'content_api.search',
    'content_api.auth',
    'content_api.publish',
    'newsroom.users',
    'newsroom.auth.oauth',
    'newsroom.companies',
    'newsroom.wire',
    'newsroom.topics',
    'newsroom.upload',
    'newsroom.history',
    'newsroom.ui_config',
    'newsroom.notifications',
    'newsroom.products',
    'newsroom.section_filters',
    'newsroom.navigations',
    'newsroom.cards',
    'newsroom.reports',
    'newsroom.public',
    'newsroom.agenda',
    'newsroom.settings',
    'newsroom.photos',
    'newsroom.media_utils',
    'newsroom.news_api',
    'newsroom.news_api.api_tokens',
    'newsroom.news_api.api_audit',
    'newsroom.monitoring',
    'newsroom.company_expiry_alerts',
    'newsroom.oauth_clients',
    'newsroom.auth_server.client',
    'newsroom.email_templates'
]

SITE_NAME = 'AAP Newsroom'
COPYRIGHT_HOLDER = 'AAP'
COPYRIGHT_NOTICE = ''
USAGE_TERMS = ''
CONTACT_ADDRESS = 'https://www.aap.com.au/contact/sales-inquiries/'
PRIVACY_POLICY = 'https://www.aap.com.au/legal/'
TERMS_AND_CONDITIONS = 'https://www.aap.com.au/legal/'
SHOW_COPYRIGHT = True
SHOW_USER_REGISTER = False

TEMPLATES_AUTO_RELOAD = True

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S+0000'

WEBPACK_ASSETS_URL = os.environ.get('WEBPACK_ASSETS_URL')
WEBPACK_SERVER_URL = os.environ.get('WEBPACK_SERVER_URL')

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
MAIL_DEFAULT_SENDER = _MAIL_FROM or 'newsroom@localhost'
# Recipients for the sign up form filled by new users (single or comma separated)
SIGNUP_EMAIL_RECIPIENTS = os.environ.get('SIGNUP_EMAIL_RECIPIENTS')

#: public client url - used to create links within emails etc
CLIENT_URL = 'http://localhost:5050'

MEDIA_PREFIX = os.environ.get('MEDIA_PREFIX', '/assets')

# Flask Limiter Settings
RATELIMIT_ENABLED = True
RATELIMIT_STRATEGY = 'fixed-window'

# Cache Settings
# https://flask-caching.readthedocs.io/en/latest/#configuring-flask-caching
CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')  # in-memory cache
# The default timeout that is used if no timeout is specified in sec
CACHE_DEFAULT_TIMEOUT = 3600
# Redis host (used only if CACHE_TYPE is redis)
CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')

# Recaptcha Settings
RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')

# Filter tab behaviour
# If true, aggregations will be against all content all the time
# If false, aggregations will change by filters applied
FILTER_BY_POST_FILTER = False

FILTER_AGGREGATIONS = True

# List of filters to remove matching stories when news only switch is turned on
NEWS_ONLY_FILTERS = [
   {'match': {'genre.code': 'Results (sport)'}},
   {'match': {'source': 'PMF'}},
]

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

GOOGLE_MAPS_KEY = os.environ.get('GOOGLE_MAPS_KEY')
GOOGLE_ANALYTICS = os.environ.get('GOOGLE_ANALYTICS')

COVERAGE_TYPES = {
    'text': {'name': 'Text', 'icon': 'text'},
    'photo': {'name': 'Photo', 'icon': 'photo'},
    'picture': {'name': 'Picture', 'icon': 'photo'},
    'audio': {'name': 'Audio', 'icon': 'audio'},
    'video': {'name': 'Video', 'icon': 'video'},
    'explainer': {'name': 'Explainer', 'icon': 'explainer'},
    'infographics': {'name': 'Infographics', 'icon': 'infographics'},
    'graphic': {'name': 'Graphic', 'icon': 'infographics'},
    'live_video': {'name': 'Live Video', 'icon': 'live-video'},
    'live_blog': {'name': 'Live Blog', 'icon': 'live-blog'},
    'video_explainer': {'name': 'Video Explainer', 'icon': 'explainer'}
}

LANGUAGES = ['en', 'fi', 'cs']
DEFAULT_LANGUAGE = 'en'

CLIENT_LOCALE_FORMATS = {
    "en": {  # defaults
        "TIME_FORMAT": "HH:mm",
        "DATE_FORMAT": "DD/MM/YYYY",
        "COVERAGE_DATE_TIME_FORMAT": "HH:mm DD/MM",
        "COVERAGE_DATE_FORMAT": "DD/MM",
        "DATE_FORMAT_HEADER": "EEEE, dd.MM.yyyy"
    },
    "fr_CA": {  # example - you can overwrite any format above
        "DATE_FORMAT": "DD/MM/YYYY",
        "DATE_FORMAT_HEADER": "EEEE, 'le' d MMMM yyyy",
    }
}

LANGUAGES = ['en', 'fi', 'cs', 'fr_CA']
DEFAULT_LANGUAGE = 'en'

CLIENT_LOCALE_FORMATS = {
    "en": {  # defaults
        "TIME_FORMAT": "HH:mm",
        "DATE_FORMAT": "DD/MM/YYYY",
        "COVERAGE_DATE_TIME_FORMAT": "HH:mm DD/MM",
        "COVERAGE_DATE_FORMAT": "DD/MM",
    },
    "fr_CA": {  # example - you can overwrite any format above
        "DATE_FORMAT": "DD/MM/YYYY",
    }
}

# Client configuration
CLIENT_CONFIG = {
    'debug': DEBUG,
    'default_language': DEFAULT_LANGUAGE,
    'locale_formats': CLIENT_LOCALE_FORMATS,
    'coverage_types': COVERAGE_TYPES,
    'list_animations': True,  # Enables or disables the animations for list item select boxes,
    'display_news_only': True,  # Displays news only switch in wire,
    'default_timezone': DEFAULT_TIMEZONE,
    'item_actions': {},
    'display_abstract': DISPLAY_ABSTRACT,
    'display_credits': False,
}

# Enable iframely support for item body_html
IFRAMELY = True

COMPANY_TYPES = []

#: celery config
WEBSOCKET_EXCHANGE = celery_queue('newsroom_notification')

CELERY_TASK_DEFAULT_QUEUE = celery_queue('newsroom')
CELERY_TASK_QUEUES = (
    Queue(celery_queue('newsroom'), Exchange(celery_queue('newsroom'), type='topic'), routing_key='newsroom.#'),
)

CELERY_TASK_ROUTES = {
    'newsroom.*': {
        'queue': celery_queue('newsroom'),
        'routing_key': 'newsroom.task',
    }
}

#: celery beat config
CELERY_BEAT_SCHEDULE = {
    'newsroom:company_expiry': {
        'task': 'newsroom.company_expiry_alerts.company_expiry',
        'schedule': crontab(hour=local_to_utc_hour(0), minute=0),  # Runs every day at midnight
    },
    'newsroom:monitoring_schedule_alerts': {
        'task': 'newsroom.monitoring.email_alerts.monitoring_schedule_alerts',
        'schedule': timedelta(seconds=60),
    },
    'newsroom:monitoring_immediate_alerts': {
        'task': 'newsroom.monitoring.email_alerts.monitoring_immediate_alerts',
        'schedule': timedelta(seconds=60),
    }
}

MAX_EXPIRY_QUERY_LIMIT = os.environ.get('MAX_EXPIRY_QUERY_LIMIT', 100)
CONTENT_API_EXPIRY_DAYS = os.environ.get('CONTENT_API_EXPIRY_DAYS', 180)

NEWS_API_ENABLED = strtobool(env('NEWS_API_ENABLED', 'false'))

# Enables the application of product filtering to image references in the API and ATOM responses
NEWS_API_IMAGE_PERMISSIONS_ENABLED = strtobool(env('NEWS_API_IMAGE_PERMISSIONS_ENABLED', 'false'))

ELASTICSEARCH_SETTINGS.setdefault("settings", {})["query_string"] = {
    # https://discuss.elastic.co/t/configuring-the-standard-tokenizer/8691/5
    'analyze_wildcard': False
}

#: server working directory
#: should be set in settings.py
SERVER_PATH = pathlib.Path(__file__).resolve().parent.parent

#: client working directory
#: used to locate client/dist/manifest.json file
CLIENT_PATH = SERVER_PATH

#: server date/time formats
#: defined using babel syntax http://babel.pocoo.org/en/latest/dates.html#date-and-time
TIME_FORMAT_SHORT = "HH:mm"
DATE_FORMAT_SHORT = "short"
DATE_FORMAT_HEADER = "EEEE, dd.MM.yyyy"
DATETIME_FORMAT_SHORT = "short"
DATETIME_FORMAT_LONG = "dd/MM/yyyy HH:mm"

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
