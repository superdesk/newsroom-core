from urllib.parse import urlparse
from superdesk.default_settings import strtobool
from newsroom.web.default_settings import (  # noqa
    env,
    ELASTICSEARCH_URL,
    ELASTICSEARCH_SETTINGS,
    CONTENTAPI_ELASTICSEARCH_URL,
    CONTENTAPI_ELASTICSEARCH_SETTINGS,
    CLIENT_URL,
    AUTH_PROVIDERS,  # Required otherwise NewsAPI behave tests fail on ``company.validate_auth_provider``
    LOG_CONFIG_FILE,
)

SITE_NAME = env("SITE_NAME", "NEWSHUB")
NEWSAPI_URL = env("NEWSAPI_URL", "http://localhost:5400")
server_url = urlparse(NEWSAPI_URL)
URL_PREFIX = env("NEWSAPI_URL_PREFIX", server_url.path.strip("/")) or "api/v1"

QUERY_MAX_PAGE_SIZE = 100

BLUEPRINTS = []

CORE_APPS = [
    "newsroom.news_api",
    "newsroom.news_api.api_tokens",
    "newsroom.companies",
    "newsroom.news_api.items",
    "content_api.items_versions",
    "newsroom.news_api.section_filters",
    "newsroom.news_api.news",
]

MODULES = [
    "newsroom.assets.module",
    ("newsroom.companies", dict(register_endpoints=False)),
    ("newsroom.history_async", dict(register_endpoints=False)),
    # Register ``settings`` module, so we can call ``get_setting`` in NewsAPI
    ("newsroom.settings", dict(register_endpoints=False, register_settings=False)),
    ("newsroom.wire.module", dict(register_endpoints=False)),
    ("newsroom.section_filters", dict(register_endpoints=False)),
    "newsroom.news_api.news.assets",
    "newsroom.news_api.news.atom",
    "newsroom.news_api.news.rss",
    "newsroom.news_api.news.search",
    "newsroom.news_api.news.feed",
    "newsroom.news_api.api_audit",
    "newsroom.news_api.news.item.item",
    ("newsroom.products", dict(register_endpoints=False)),
    "newsroom.news_api.products",
]

INSTALLED_APPS = []

LANGUAGES = ["en", "fi", "cs", "fr_CA"]
DEFAULT_LANGUAGE = "en"

# newsroom default db and index names
MONGO_DBNAME = env("MONGO_DBNAME", "newsroom")
# mongo
MONGO_URI = env("MONGO_URI", f"mongodb://localhost/{MONGO_DBNAME}")
CONTENTAPI_MONGO_URI = env("CONTENTAPI_MONGO_URI", f"mongodb://localhost/{MONGO_DBNAME}")
# elastic
ELASTICSEARCH_INDEX = env("ELASTICSEARCH_INDEX", MONGO_DBNAME)
CONTENTAPI_ELASTICSEARCH_INDEX = env("CONTENTAPI_ELASTICSEARCH_INDEX", MONGO_DBNAME)

FILTER_AGGREGATIONS = False
ELASTIC_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
ELASTICSEARCH_FIX_QUERY = False

# Disable upload endpoint from ``newsroom.assets.module``,
# as NewsAPI will implement a custom one
ASSETS_REGISTER_UPLOAD_ENDPOINT = False

ASYNC_AUTH_CLASS = "newsroom.news_api.api_tokens.auth:CompanyTokenAuth"

WIRE_EMBED_PERMISSIONS = strtobool(env("WIRE_EMBED_PERMISSIONS", True))
