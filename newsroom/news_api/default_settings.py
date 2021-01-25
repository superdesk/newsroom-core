import os

from superdesk.default_settings import ( # noqa
    env,
    ELASTICSEARCH_URL,
    CONTENTAPI_ELASTICSEARCH_URL
)

URL_PREFIX = os.environ.get('CONTENT_API_PREFIX', 'api/v1')
QUERY_MAX_PAGE_SIZE = 100

BLUEPRINTS = []

CORE_APPS = [
    'newsroom.news_api',
    'newsroom.news_api.api_tokens',
    'newsroom.companies',
    'newsroom.news_api.items',
    'content_api.items_versions',
    'newsroom.news_api.section_filters',
    'newsroom.news_api.products',
    'newsroom.news_api.formatters',
    'newsroom.news_api.news',
    'newsroom.news_api.news.item.item',
    'newsroom.news_api.news.search',
    'newsroom.news_api.news.feed',
    'newsroom.products',
    'newsroom.news_api.api_audit',
    'newsroom.news_api.news.assets.assets',
    'newsroom.upload',
    'newsroom.news_api.news.atom.atom',
    'newsroom.history'
]

INSTALLED_APPS = []

LANGUAGES = ['en', 'fi', 'cs', 'fr_CA']
DEFAULT_LANGUAGE = 'en'

# newsroom default db and index names
MONGO_DBNAME = env('MONGO_DBNAME', 'newsroom')
# mongo
MONGO_URI = env('MONGO_URI', f'mongodb://localhost/{MONGO_DBNAME}')
CONTENTAPI_MONGO_URI = env('CONTENTAPI_MONGO_URI', f'mongodb://localhost/{MONGO_DBNAME}')
# elastic
ELASTICSEARCH_INDEX = env('ELASTICSEARCH_INDEX', MONGO_DBNAME)
CONTENTAPI_ELASTICSEARCH_INDEX = env('CONTENTAPI_ELASTICSEARCH_INDEX', MONGO_DBNAME)


FILTER_AGGREGATIONS = False
ELASTIC_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
